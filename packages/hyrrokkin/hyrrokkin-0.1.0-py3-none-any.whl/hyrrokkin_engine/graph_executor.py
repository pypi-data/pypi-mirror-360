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

import asyncio
import threading
import logging
from collections import defaultdict
import time
import queue

from .graph_link import GraphLink
from .node_service import NodeService
from .node_wrapper import NodeWrapper
from .configuration_service import ConfigurationService
from .configuration_wrapper import ConfigurationWrapper
from .package_type import PackageType

class GraphExecutor():

    def __init__(self, execution_limit=4,
                 execution_monitor_callback=None,
                 status_callback=None,
                 node_execution_callback=None,
                 message_callback=None,
                 output_notification_callback=None,
                 request_open_client_callback=None):

        self.node_outputs = {}
        self.node_wrappers = {}
        self.configuration_wrappers = {}
        self.execution_limit = execution_limit
        self.injected_inputs = {}
        self.output_listeners = {}

        self.target_queues = {"node": {}, "configuration": {}}
        self.target_queue_pending = 0
        self.target_queue_dispatch_on_empty = False
        self.target_is_handling = {"node": set(), "configuration": set()}

        self.execution_running = False

        self.execution_monitor_callback = execution_monitor_callback
        self.status_callback = status_callback
        self.node_execution_callback = node_execution_callback
        self.message_callback = message_callback
        self.output_notification_callback = output_notification_callback
        self.request_open_client_callback = request_open_client_callback

        self.package_schemas = {} # package_id => schema
        self.node_types = {} # node_id => node-type-id
        self.package_folders = {} # package_id => package folder (path to folder containing package's schema)


         # new state

        self.links = {}  # link-id = > GraphLink
        self.out_links = {}  # node-id = > output-port = > [GraphLink]
        self.in_links = {}  # node-id = > input-port = > [GraphLink]

        self.dirty_nodes = {}  # node-id => True
        self.executing_nodes = {}  # node-id => True
        self.executed_nodes = {} # node-id => True
        self.failed_nodes = {} # node-id => Exception

        self.executing_tasks = set()

        self.lock = threading.Lock()

        self.paused = True
        self.terminate_on_complete = False

        self.is_executing = {}
        self.execution_states = {}

        self.logger = logging.getLogger("ExecutionThread")

        self.failed = False

    async def pause(self):
        self.paused = True

    async def resume(self, after_message_delivery=False):
        self.paused = False
        if after_message_delivery and self.target_queue_pending > 0:
            self.target_queue_dispatch_on_empty = True
        else:
            self.dispatch()

    def queue_target(self, target_id, target_type, coro):
        target_queue = self.target_queues[target_type]
        if target_id not in target_queue:
            target_queue[target_id] = queue.Queue()
        target_queue[target_id].put(coro)
        self.target_queue_pending += 1
        if target_id not in self.target_is_handling[target_type]:
            self.dispatch_target(target_id, target_type)

    def dispatch_target(self, target_id, target_type):
        coro = self.target_queues[target_type][target_id].get()
        self.target_is_handling[target_type].add(target_id)
        task = asyncio.create_task(self.execute_target(target_id, target_type, coro))
        task.add_done_callback(self.executing_tasks.discard)
        self.executing_tasks.add(task)

    async def execute_target(self, target_id, target_type, coro):
        await coro()
        self.target_queue_pending -= 1
        self.target_is_handling[target_type].remove(target_id)
        if not self.target_queues[target_type][target_id].empty():
            self.dispatch_target(target_id, target_type)
        if self.target_queue_pending == 0 and self.target_queue_dispatch_on_empty:
            self.target_queue_dispatch_on_empty = False
            self.dispatch()

    async def add_package(self,package_id, schema, package_folder, configuration_instance):
        self.package_schemas[package_id] = PackageType.load(schema)
        self.package_folders[package_id] = package_folder
        await self.configuration_wrappers[package_id].set_instance(configuration_instance)

    async def add_node(self, node_id, instance):
        await self.node_wrappers[node_id].set_instance(instance)
        await self.mark_dirty(node_id)
        self.dispatch()

    async def remove_node(self, node_id):
        if node_id in self.node_wrappers:
            self.node_wrappers[node_id].remove()
            del self.node_wrappers[node_id]
        if node_id in self.node_outputs:
            del self.node_outputs[node_id]
        if node_id in self.dirty_nodes:
            del self.dirty_nodes[node_id]
        if node_id in self.failed_nodes:
            del self.failed_nodes[node_id]
        if node_id in self.in_links:
            del self.in_links[node_id]
        if node_id in self.out_links:
            del self.out_links[node_id]
        if node_id in self.node_types:
            del self.node_types[node_id]

    def add_output_listener(self, node_id, output_port_name):
        if node_id not in self.output_listeners:
            self.output_listeners[node_id] = set()
        self.output_listeners[node_id].add(output_port_name)

    def remove_output_listener(self, node_id, output_port_name):
        if node_id in self.output_listeners:
            if output_port_name in self.output_listeners[node_id]:
                self.output_listeners[node_id].remove(output_port_name)

    def get_outputs_from(self, output_node_id):
        input_node_ports = []
        node_out_links = self.out_links.get(output_node_id, {})
        for (output_port, link_list) in node_out_links.items():
            for link in link_list:
                input_node_ports.append((link.to_node_id, link.to_port))
        return input_node_ports

    def get_inputs_to(self, input_node_id):
        output_node_ports = []
        node_in_links = self.in_links.get(input_node_id, {})
        for (input_port, link_list) in node_in_links.items():
            for link in link_list:
                output_node_ports.append((link.from_node_id, link.from_port))
        return output_node_ports

    async def add_link(self, link_id, from_node_id, from_port, to_node_id, to_port, loading=False):
        graph_link = GraphLink(self,from_node_id,from_port,to_node_id,to_port)
        self.links[link_id] = graph_link
        if to_node_id not in self.in_links:
            self.in_links[to_node_id] = defaultdict(list)
        self.in_links[to_node_id][to_port].append(graph_link)
        if from_node_id not in self.out_links:
            self.out_links[from_node_id] = defaultdict(list)
        self.out_links[from_node_id][from_port].append(graph_link)

        if not loading:
            await self.mark_dirty(to_node_id)
            self.dispatch()

    async def remove_link(self, link_id):
        link = self.links[link_id]

        self.in_links[link.to_node_id][link.to_port].remove(link)
        self.out_links[link.from_node_id][link.from_port].remove(link)
        del self.links[link_id]

        await self.mark_dirty(link.to_node_id)
        self.dispatch()

    async def inject_input(self, node_id, input_port_name, injected_value):
        self.injected_inputs = {}
        injected_node_ids = set()
        if injected_value is None:
            if node_id in self.injected_inputs:
                if input_port_name in self.injected_inputs[node_id]:
                    del self.injected_inputs[node_id][input_port_name]
        else:
            if node_id not in self.injected_inputs:
                self.injected_inputs[node_id] = {}
            self.injected_inputs[node_id][input_port_name] = injected_value

        await self.mark_dirty(node_id)

    async def clear(self):
        node_ids = list(self.node_wrappers.keys())
        for node_id in node_ids:
            self.node_wrappers[node_id].remove()
        self.links = {}
        self.in_links = {}
        self.out_links = {}

    def open_session(self, session_id):
        for wrapper in self.configuration_wrappers.values():
            wrapper.open_session(session_id)

    def close_session(self, session_id):
        for wrapper in self.configuration_wrappers.values():
            wrapper.close_session(session_id)

    async def open_client(self, target_id, target_type, session_id, client_id, client_options):

        async def action_coro():
            if target_type == "node":
                wrapper = self.node_wrappers.get(target_id,None)
            elif target_type == "configuration":
                wrapper = self.configuration_wrappers.get(target_id, None)
            else:
                self.logger.error(f"invalid target_type: {target_type}")
                return
            if wrapper is not None:
                await wrapper.open_client(session_id, client_id, client_options)

        self.queue_target(target_id, target_type, action_coro)

    async def recv_message(self, target_id, target_type, session_id, client_id, *msg):

        async def action_coro():
            if target_type == "node":
                wrapper = self.node_wrappers.get(target_id,None)
            elif target_type == "configuration":
                wrapper = self.configuration_wrappers.get(target_id,None)
            else:
                self.logger.error(f"invalid target_type: {target_type}")
                return

            if wrapper is not None:
                await wrapper.recv_message(session_id, client_id, *msg)

        self.queue_target(target_id, target_type, action_coro)

    async def close_client(self, target_id, target_type, session_id, client_id):

        async def action_coro():
            print("close_client")
            if target_type == "node":
                wrapper = self.node_wrappers.get(target_id, None)
            elif target_type == "configuration":
                wrapper = self.configuration_wrappers.get(target_id, None)
            else:
                self.logger.error(f"invalid target_type: {target_type}")
                return
            if wrapper is not None:
                await wrapper.close_client(session_id, client_id)

        self.queue_target(target_id, target_type, action_coro)

    async def create_node_service(self, node_id, node_type_id, package_id, persistence):
        service = NodeService(node_id, self.package_folders[package_id])

        self.node_types[node_id] = node_type_id

        (package_id, _) = node_type_id.split(":")

        persistence.configure(node_id, "node")

        async def request_run_cb():
            await self.request_run(node_id)

        node_wrapper = NodeWrapper(persistence, node_id, package_id, service,
                                   get_configuration_wrapper_fn=lambda package_id: self.get_configuration_wrapper(package_id),
                                   set_status_cb=lambda status_state, message: self.set_status(node_id, "node", status_state, message),
                                   set_execution_state_cb=lambda running_state, is_manual: self.set_node_running_state(node_id, running_state=running_state, is_manual=is_manual),
                                   request_run_cb=request_run_cb,
                                   send_message_cb=lambda session_id, client_id, *message: self.send_message(node_id, "node", session_id, client_id, *message),
                                   request_open_client_cb=lambda client_name, session_id: self.request_open_client(node_id, "node", session_id, client_name))
        self.node_wrappers[node_id] = node_wrapper
        self.is_executing[node_id] = 0
        return service

    async def create_configuration_service(self, package_id, package_folder, persistence):
        services = ConfigurationService(package_id, package_folder)
        persistence.configure(package_id, "configuration")
        configuration_wrapper = ConfigurationWrapper(persistence, package_id, services,
                    get_configuration_wrapper_fn=lambda package_id :self.get_configuration_wrapper(package_id),
                    set_status_cb=lambda status_state, message: self.set_status(package_id, "configuration", status_state, message),
                    send_message_cb=lambda session_id, client_id, *message: self.send_message(package_id, "configuration", session_id, client_id, *message),
                    request_open_client_cb=lambda client_name, session_id: self.request_open_client(package_id, "configuration", session_id, client_name))
        services.set_wrapper(configuration_wrapper)
        self.configuration_wrappers[package_id] = configuration_wrapper
        return services

    def executing_node_count(self):
        return len(self.executing_nodes)

    async def mark_dirty(self, node_id):

        if node_id in self.dirty_nodes:
            return

        self.dirty_nodes[node_id] = True

        if node_id in self.executed_nodes:
            del self.executed_nodes[node_id]
        if node_id in self.failed_nodes:
            del self.failed_nodes[node_id]

        self.set_node_running_state(node_id, "pending")
        await self.reset_run(node_id)

        # mark all downstream nodes as dirty

        outputs = self.get_outputs_from(node_id)
        for (to_node_id, _) in outputs:
            await self.mark_dirty(to_node_id)

    def dispatch(self):
        if self.paused:
            return

        launch_nodes = []
        launch_limit = (self.execution_limit - self.executing_node_count())

        if launch_limit > 0:
            for node_id in self.dirty_nodes:
                if self.can_execute(node_id):
                    launch_nodes.append(node_id)

                if len(launch_nodes) >= launch_limit:
                    break

        if len(self.executing_nodes) == 0 and len(launch_nodes) > 0:
            self.execution_started()

        for node_id in launch_nodes:
            del self.dirty_nodes[node_id]
            self.executing_nodes[node_id] = True
            task = asyncio.create_task(self.execute(node_id))
            task.add_done_callback(self.executing_tasks.discard)
            self.executing_tasks.add(task)

        if len(self.executing_nodes) == 0:
            self.execution_complete()


    def can_execute(self, node_id):
        if node_id in self.executing_nodes:
            return False
        for (output_node_id, output_port) in self.get_inputs_to(node_id):
            if output_node_id not in self.executed_nodes:
                return False
        return True

    def pre_execute(self, node_id):
        inputs = {}
        node_type_id = self.node_types[node_id]
        (package_id, node_type_name) = node_type_id.split(":")
        node_type = self.package_schemas[package_id].get_node_type(node_type_name)
        # collect together the input values at each input port
        # start with output values from connected ports

        in_links = self.in_links.get(node_id, {})
        for input_port_name in in_links:
            allow_multiple_connections = node_type.allow_multiple_input_connections(input_port_name)
            if len(in_links[input_port_name]) > 0:
                if allow_multiple_connections:
                    inputs[input_port_name] = []
                    for link in in_links[input_port_name]:
                        if link.has_value():
                            inputs[input_port_name].append(link.get_value())
                else:
                    if in_links[input_port_name][0].has_value():
                        inputs[input_port_name] = in_links[input_port_name][0].get_value()

        # add in any injected input values
        if node_id in self.injected_inputs:
            for injected_input_port_name in self.injected_inputs[node_id]:
                allow_multiple_connections = node_type.allow_multiple_input_connections(injected_input_port_name)
                package_id,link_type = node_type.get_input_link_type(injected_input_port_name).split(":")
                configuration_wrapper = self.configuration_wrappers[package_id]
                injected_value = configuration_wrapper.decode(self.injected_inputs[node_id][injected_input_port_name],link_type)
                if allow_multiple_connections:
                    if injected_input_port_name not in inputs:
                        inputs[injected_input_port_name] = []
                    inputs[injected_input_port_name] += injected_value
                else:
                    inputs[injected_input_port_name] = injected_value

        return inputs

    async def execute(self, node_id):
        inputs = self.pre_execute(node_id)
        try:
            node_wrapper = self.node_wrappers[node_id]
            self.set_node_running_state(node_id, "running")
            results = await node_wrapper.execute(inputs)
            if results is None:
                results = {}
            self.set_node_running_state(node_id, "completed")
            self.post_execute(node_id, results, None)
        except Exception as ex:
            self.set_node_running_state(node_id, "failed", ex)
            self.post_execute(node_id, None, ex)

        self.dispatch()

    def post_execute(self, node_id, result, exn):
        if node_id in self.executing_nodes:
            del self.executing_nodes[node_id]
        if node_id in self.node_outputs:
            del self.node_outputs[node_id]
        if exn is not None:
            self.failed_nodes[node_id] = exn
        else:
            self.executed_nodes[node_id] = True

        node_type_id = self.node_types[node_id]
        (package_id, node_type_name) = node_type_id.split(":")
        node_type = self.package_schemas[package_id].get_node_type(node_type_name)

        if result is not None:
            self.node_outputs[node_id] = {}

            for port_name in result:
                self.node_outputs[node_id][port_name] = result[port_name]

            if node_id in self.output_listeners and self.output_notification_callback:
                for port_name in result:
                    if port_name in self.output_listeners[node_id]:
                        value = result[port_name]
                        (package_id,link_type) = node_type.get_output_link_type(port_name).split(":")
                        encoded_bytes = self.configuration_wrappers[package_id].encode(value,link_type)
                        self.output_notification_callback(node_id, port_name, encoded_bytes)

    async def reset_run(self, node_id):
        await self.node_wrappers[node_id].reset_run()

    async def request_run(self, node_id):
        await self.mark_dirty(node_id)
        self.dispatch()

    def execution_started(self):
        if not self.execution_running:
            self.execution_running = True
            if self.execution_monitor_callback:
                self.execution_monitor_callback(False)

    def execution_complete(self):
        if self.execution_running:
            self.execution_running = False
            if self.execution_monitor_callback:
                self.execution_monitor_callback(True)

    def request_open_client(self, target_id, target_type, session_id, client_name):
        if self.request_open_client_callback:
            self.request_open_client_callback(target_id, target_type, session_id, client_name)

    def get_configuration_wrapper(self, package_id):
        return self.configuration_wrappers.get(package_id,None)

    def set_status(self, origin_id, origin_type, state, message):
        if self.status_callback:
            self.status_callback(origin_id, origin_type, message, state)

    def set_node_running_state(self, node_id, running_state, exn=None, is_manual=False):
        at_time = time.time()
        if self.node_execution_callback:
            self.node_execution_callback(at_time, node_id, running_state, exn, is_manual)

    def send_message(self, origin_id, origin_type, session_id, client_id, *msg):
        if self.message_callback:
            self.message_callback(origin_id, origin_type, session_id, client_id, *msg)

    def count_failed(self):
        return len(self.failed_nodes)

    def close(self):
        pass








