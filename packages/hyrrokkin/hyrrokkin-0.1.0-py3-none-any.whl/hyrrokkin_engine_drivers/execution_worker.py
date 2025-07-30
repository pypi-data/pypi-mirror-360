#   Hyrrokkin - a library for building and running executable graphs
#
#   MIT License - Copyright (C) 2022-2025  Visual Topology Ltd
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy of this software
#   and associated documentation files (the "Software"), to deal in the Software without
#   restriction, including without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#   BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#   NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
import queue
import sys
import os
import signal
import logging
import asyncio
import traceback
import time
import importlib
import json

from hyrrokkin_engine.registry import registry
from hyrrokkin_engine.message_utils import MessageUtils
from hyrrokkin_engine.graph_executor import GraphExecutor
from hyrrokkin_engine_drivers.persistence_memory import PersistenceMemory
from hyrrokkin_engine_drivers.persistence_filesystem import PersistenceFileSystem

class ExecutionWorker:

    MAX_RETRIES = 4
    RETRY_DELAY_MS = 1000

    def __init__(self, host_name, port, verbose):

        self.host_name = host_name
        self.port = port
        self.verbose = verbose
        self.pid = os.getpid()

        self.reader = None
        self.writer = None
        self.graph_executor = None
        self.injected_inputs = {}
        self.output_listeners = {}
        self.persistence = {}

        self.running = False
        self.read_only = False

    async def run(self):
        retry = 0
        while True:
            try:
                self.reader, self.writer = await asyncio.open_connection(self.host_name, self.port)
                break
            except Exception as ex:
                retry += 1
                if retry > self.MAX_RETRIES:
                    raise ex
                time.sleep(self.RETRY_DELAY_MS/1000)

        msg = await self.receive_message()
        control_packet = msg[0]
        action = control_packet["action"]

        if self.verbose:
            print("Worker <- "+ json.dumps(control_packet))

        if action == "init":
            self.init(control_packet)
        else:
            raise Exception("Protocol error")

        self.running = True
        while self.running:
            try:
                msg = await self.receive_message()
                if msg is None:
                    break
                try:
                    await self.handle_message(*msg)
                except:
                    traceback.print_exc()
            except:
                self.running = False
        self.graph_executor.close()
        self.writer.close()
        await self.writer.wait_closed()

    async def send_message(self, *message_parts):
        self.send_message_sync(*message_parts)
        await self.writer.drain()

    def send_message_sync(self, *message_parts):
        if self.verbose:
            print("Worker -> "+ json.dumps(message_parts[0]))
        message_bytes = MessageUtils.encode_message(*message_parts)
        self.writer.write(len(message_bytes).to_bytes(4, "big"))
        self.writer.write(message_bytes)

    async def receive_message(self):
        message_length_bytes = await self.reader.read(4)
        if message_length_bytes == 0:
            return None
        message_length = int.from_bytes(message_length_bytes, "big")
        message_bytes = await self.reader.read(message_length)
        message_parts = MessageUtils.decode_message(message_bytes)
        return message_parts

    def get_persistence(self, target_id, target_type):
        key = target_id+":"+target_type
        if key in self.persistence:
            return self.persistence[key]
        if self.execution_folder:
            persistence = PersistenceFileSystem(root_folder=self.execution_folder, read_only=False)
        else:
            persistence = PersistenceMemory()
        persistence.configure(target_id, target_type)
        self.persistence[key] = persistence
        return persistence

    def remove_persistence(self, target_id, target_type):
        key = target_id + ":" + target_type;
        if key in self.persistence:
            del self.persistence[key]

    async def load_target(self, o, properties, *datalist):
        target_id = o["target_id"]
        target_type = o["target_type"]
        datakeys = o["datakeys"]
        persistence = self.get_persistence(target_id,target_type)
        await persistence.set_properties(properties)
        for idx in range(0,len(datakeys)):
            await persistence.set_data(datakeys[idx],datalist[idx])

    async def add_node(self,o):
        node_id = o["node_id"]
        node_type_id = o["node_type_id"]
        package_id = node_type_id.split(":")[0]
        persistence = self.get_persistence(node_id,"node")
        service = await self.graph_executor.create_node_service(node_id, node_type_id, package_id, persistence)
        configuration_wrapper = self.graph_executor.get_configuration_wrapper(package_id)
        instance = await configuration_wrapper.create_node(node_type_id.split(":")[1], service)
        await self.graph_executor.add_node(o["node_id"], instance)

    async def add_package(self,o):
        package_id = o["package_id"]
        package_folder = o["folder"]
        persistence = self.get_persistence(package_id,"configuration")
        services = await self.graph_executor.create_configuration_service(package_id, package_folder, persistence)
        instance = registry.create_configuration(package_id, services)
        await self.graph_executor.add_package(o["package_id"], o["schema"], package_folder,instance)
        
    async def handle_message(self, control_packet, *extras):
        if self.verbose:
            print("Worker <- "+ json.dumps(control_packet))
        action = control_packet["action"]
        if action == "add_package":
            await self.add_package(control_packet)
        elif action == "packages_added":
            self.send_message_sync({"action":"init_complete"})
        elif action == "add_node":
            await self.add_node(control_packet)
        elif action == "load_target":
            await self.load_target(control_packet, *extras)
        elif action == "add_link":
            await self.graph_executor.add_link(control_packet["link_id"],control_packet["from_node_id"],control_packet["from_port"],
                                         control_packet["to_node_id"], control_packet["to_port"], control_packet["loading"])
        elif action == "inject_input":
            await self.graph_executor.inject_input(control_packet["node_id"], control_packet["input_port_name"], extras[0])
        elif action == "add_output_listener":
            self.graph_executor.add_output_listener(control_packet["node_id"], control_packet["output_port_name"])
        elif action == "remove_output_listener":
            self.graph_executor.remove_output_listener(control_packet["node_id"], control_packet["output_port_name"])
        elif action == "pause":
            await self.graph_executor.pause()
        elif action == "resume":
            await self.graph_executor.resume(control_packet["after_message_delivery"])
        elif action == "close":
            self.running = False
        elif action == "open_session":
            session_id = control_packet["session_id"]
            self.graph_executor.open_session(session_id)
        elif action == "close_session":
            session_id = control_packet["session_id"]
            self.graph_executor.close_session(session_id)
        elif action == "open_client":
            session_id = control_packet["session_id"]
            client_id = control_packet["client_id"]
            await self.graph_executor.open_client(control_packet["target_id"],
                                    control_packet["target_type"],
                                    session_id,
                                    client_id,
                                    control_packet["client_options"])
        elif action == "client_message":
            session_id = control_packet["session_id"]
            client_id = control_packet["client_id"]
            await self.graph_executor.recv_message(control_packet["target_id"],
                                    control_packet["target_type"],
                                    session_id,
                                    client_id,
                                    *extras)
        elif action == "close_client":
            session_id = control_packet["session_id"]
            client_id = control_packet["client_id"]
            await self.graph_executor.close_client(control_packet["target_id"],
                                    control_packet["target_type"],
                                    session_id,
                                    client_id)
        elif action == "remove_node":
            await self.graph_executor.remove_node(control_packet["node_id"])
            self.remove_persistence(control_packet["node_id"],"node")
        elif action == "remove_link":
            await self.graph_executor.remove_link(control_packet["link_id"])
        elif action == "clear":
            await self.graph_executor.clear()

    def forward_output_value(self, node_id, output_port, encoded_value_bytes):
        self.send_message_sync({"action":"output_notification", "node_id": node_id, "output_port_name":output_port},
                               encoded_value_bytes)

    def execution_monitor(self, is_complete):
        if is_complete:
            self.send_message_sync({"action":"execution_complete", "count_failed": self.graph_executor.count_failed()})
        else:
            self.send_message_sync({"action": "execution_started"})

    def set_status(self, origin_id, origin_type, state, message):
        self.send_message_sync({"action":"update_status", "origin_id":origin_id, "origin_type":origin_type, "status":state, "message":message})

    def set_node_execution_state(self, at_time, node_id, execution_state, exn=None, is_manual=False):
        self.send_message_sync({"action": "update_execution_state",
                                "at_time": at_time,
                                "node_id": node_id,
                                "execution_state": execution_state,
                                "is_manual": is_manual,
                                "exn": None if exn is None else str(exn)})



    def send_client_message(self, origin_id, origin_type, session_id, client_id, *msg):
        self.send_message_sync({"action": "client_message", "origin_id":origin_id, "origin_type":origin_type, "session_id":session_id, "client_id":client_id},*msg)

    def send_request_open_client_callback(self, origin_id, origin_type, session_id, client_name):
        self.send_message_sync(
            {"action": "request_open_client", "origin_id": origin_id, "origin_type": origin_type,
             "session_id":session_id, "client_name": client_name})

    def init(self, control_packet):
        self.read_only = control_packet["read_only"]
        self.execution_folder = control_packet["execution_folder"]
        execution_limit = control_packet["execution_limit"]
        worker_configuration = control_packet["worker_configuration"]
        for package_id in worker_configuration["packages"]:
            configuration_path = worker_configuration["packages"][package_id]["configuration_class"]
            configuration_module = importlib.import_module(".".join(configuration_path.split(".")[:-1]))
            configuration_class = getattr(configuration_module, configuration_path.split(".")[-1])
            registry.register_configuration_factory(package_id,
                lambda configuration_services: configuration_class(configuration_services))


        self.graph_executor = GraphExecutor(
                                    execution_limit=execution_limit,
                                    execution_monitor_callback=lambda is_complete: self.execution_monitor(is_complete),
                                    status_callback=lambda *args: self.set_status(*args),
                                    node_execution_callback=lambda *args: self.set_node_execution_state(*args),
                                    message_callback=lambda *args: self.send_client_message(*args),
                                    output_notification_callback=lambda *args: self.forward_output_value(*args),
                                    request_open_client_callback=lambda *args: self.send_request_open_client_callback(*args))




def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("host",type=str,help="host name")
    parser.add_argument("port",type=int,help="port number")
    parser.add_argument("verbose", type=str, choices=("verbose","quiet"), help="verbose or quiet")

    args = parser.parse_args()
    os.putenv('PYTHONPATH',os.getcwd())

    if os.getenv("DEBUG") is not None:
        logging.basicConfig(level=logging.INFO)

    server = ExecutionWorker(args.host,args.port,args.verbose=="verbose")

    def handler(signum, frame):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)

    signal.signal(3, handler)

    asyncio.run(server.run())

if __name__ == '__main__':
    main()




