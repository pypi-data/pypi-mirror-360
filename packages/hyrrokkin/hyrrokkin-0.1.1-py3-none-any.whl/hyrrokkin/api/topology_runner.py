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

from typing import Callable
import uuid
import threading
import logging
import os

from .client import Client
from hyrrokkin.execution_manager.execution_manager import ExecutionManager

from hyrrokkin.execution_manager.execution_client import ExecutionClient
from hyrrokkin.engine_launchers.javascript_engine_launcher import JavascriptEngineLauncher
from hyrrokkin.engine_launchers.python_engine_launcher import PythonEngineLauncher

def threadsafe(func):
    """
    Decorator that serialises access to a methods from multiple threads
    :param func: the method to be decorated
    :return: wrapped method
    """
    def threadsafe_wrapper(self, *args, **kwargs):
        try:
            self.lock.acquire()
            return func(self, *args, **kwargs)
        finally:
            self.lock.release()
    return threadsafe_wrapper

def check_closed(func):
    """
    Decorator that prevents access to a method once the closed attribute is set to True
    :param func: the method to be decorated
    :return: wrapped method
    """
    def threadsafe_wrapper(self, *args, **kwargs):
        if self.closed:
            raise Exception("Runner is closed")
        return func(self, *args, **kwargs)
    return threadsafe_wrapper

class TopologyRunner:

    def __init__(self, network, schema, execution_folder, engine_launcher, status_event_handler, execution_event_handler, read_only):

        self.network = network
        self.schema = schema

        self.closed = False
        self.close_handler = None

        self.logger = logging.getLogger("topology_runner")

        self.add_node_callback = None
        self.add_link_callback = None
        self.remove_node_callback = None
        self.remove_link_callback = None
        self.clear_network_callback = None

        if engine_launcher is None:
            # try to work out which engine to run
            for candidate_launcher in [PythonEngineLauncher(), JavascriptEngineLauncher()]:
                valid = True
                for package_id in schema.get_packages():
                    folder = schema.get_package_path(package_id)
                    if not os.path.exists(os.path.join(folder, candidate_launcher.get_configuration_filename())):
                        valid = False
                if valid:
                    engine_launcher = candidate_launcher
                    break

        self.paused = False

        self.lock = threading.RLock()
        self.thread = None

        self.executor = ExecutionManager(schema, execution_folder=execution_folder,
                                         status_callback=status_event_handler,
                                         node_execution_callback=execution_event_handler,
                                         engine_launcher=engine_launcher,
                                         read_only=read_only,
                                         client_message_handler=lambda *args: self.__handle_client_message(*args))

        self.executor.set_request_open_client_callback(lambda origin_id, origin_type, session_id, client_name: self.__request_open_client(origin_id, origin_type, session_id, client_name))

        self.session_ids = set()

        self.open_client_request_handler = None

        self.execution_result = None

        self.execution_clients = {}

        for (package_id, package) in self.schema.get_packages().items():
            engine_launcher.configure_package(package_id, schema.get_package_resource(package_id), schema.get_package_path(package_id))

        self.executor.init()

        for (package_id, package) in self.schema.get_packages().items():
            self.executor.add_package(package_id, package.get_schema(),
                                      self.schema.get_package_path(package_id))

        if not self.network.savedir:

            # if not disk-based, upload the properties and data for each node
            def extract_properties_data(dsu):
                properties = dsu.get_properties()
                data = {}
                for key in dsu.get_data_keys():
                    data[key] = dsu.get_data(key)
                return properties, data

            for package_id in self.schema.get_packages():
                dsu = self.network.get_configuration_datastore(package_id)
                properties, data = extract_properties_data(dsu)
                self.executor.load_target(package_id, "configuration", properties, data)

            for node_id in self.network.get_node_ids():
                dsu = self.network.get_node_datastore(node_id)
                properties, data = extract_properties_data(dsu)
                self.executor.load_target(node_id, "node", properties, data)

        # load all nodes and links into the execution

        for node_id in self.network.get_node_ids():
            self.executor.add_node(self.network.get_node(node_id), loading=True)

        for link_id in self.network.get_link_ids():
            self.executor.add_link(self.network.get_link(link_id), loading=True)





        # listen for further network changes and update the execution accordingly

        self.add_node_callback = self.network.register_add_node_callback(lambda node: self.__add_node(node))
        self.add_link_callback = self.network.register_add_link_callback(lambda link: self.__add_link(link))

        self.remove_node_callback = self.network.register_remove_node_callback(
            lambda node: self.__remove_node(node))
        self.remove_link_callback = self.network.register_remove_link_callback(
            lambda link: self.__remove_link(link))

        self.clear_network_callback = self.network.register_clear_network_callback(lambda: self.__clear())

        for session_id in self.session_ids:
            self.executor.open_session(session_id)

        for (target_id, target_type, session_id, client_id) in self.execution_clients:
            client = self.execution_clients[(target_id, target_type, session_id, client_id)]
            self.executor.connect_client(target_id, target_type, session_id, client_id, client)

    @check_closed
    @threadsafe
    def inject_input_value(self, node_id, input_port_name, value):
        """
        Inject input values into the topology.
        """
        self.executor.inject_input_value(node_id, input_port_name, value)

    @check_closed
    @threadsafe
    def add_output_listener(self, node_id, output_port_name, listener):
        self.executor.add_output_listener(node_id, output_port_name, listener)

    @check_closed
    @threadsafe
    def remove_output_listener(self, node_id, output_port_name):
        self.executor.remove_output_listener(node_id, output_port_name)

    @check_closed
    @threadsafe
    def open_session(self, session_id=None):
        if not session_id:
            session_id = str(uuid.uuid4())
        if session_id in self.session_ids:
            raise ValueError(f"session {session_id} is already open")
        else:
            self.session_ids.add(session_id)
            self.executor.open_session(session_id)
        return session_id

    @check_closed
    @threadsafe
    def close_session(self, session_id):
        if session_id in self.session_ids:
            self.session_ids.remove(session_id)
            self.executor.close_session(session_id)
        else:
            raise ValueError(f"session {session_id} is not open")

    @check_closed
    @threadsafe
    def set_request_open_client_callback(self, open_client_request_handler: Callable[[str,str,str,str],None]):
        """
        Attach a function that will be called when a node requests that a client be attached

        Args:
            open_client_request_handler: function that is called with the origin_id, origin_type, session_id, client_name as parameters
        """
        self.open_client_request_handler = open_client_request_handler

    @check_closed
    @threadsafe
    def set_execution_complete_callback(self, execution_complete_callback: Callable[[], None]):
        """
        Attach a function that will be called whenever execution of the topology completes

        Args:
            execution_complete_callback: function that will be called
        """
        self.executor.set_execution_complete_callback(execution_complete_callback)

    @check_closed
    @threadsafe
    def attach_node_client(self, node_id: str, session_id: str, client_id: str, client_options: dict = {}) -> Client:
        """
        Attach a client instance to a node.  Any client already attached to the node with the same client_id
        will be detached.

        Args:
            node_id: the node to which the client is to be attached
            session_id: the id of an opened interactive session
            client_id: the name of the client to attach, as defined in the node's schema
            client_options: optional, a dictionary with extra parameters from the client

        Returns:
             an object which implements the Client API and provides methods to interact with the client

        """
        if session_id not in self.session_ids:
            raise ValueError(f"session {session_id} is not open")
        client = Client()
        execution_client = ExecutionClient(lambda *args: self.__forward_client_message(*args),
                                           node_id, "node", session_id, client_id, client,
                                           client_options)
        self.execution_clients[(node_id, "node", session_id, client_id)] = execution_client
        self.executor.attach_client(node_id, "node", session_id, client_id, execution_client)
        return client

    @check_closed
    @threadsafe
    def detach_node_client(self, node_id: str, session_id:str, client_id: str):
        """
        Detach a client instance from a node

        Args:
            node_id: the node to which the client is to be attached
            session_id: the id of an opened interactive session
            client_id: the id of the client to detach
        """
        if (node_id, "node", session_id, client_id) in self.execution_clients:
            client = self.execution_clients[(node_id, "node", session_id, client_id)]
            self.executor.detach_client(node_id, "node", session_id, client_id, client)
            del self.execution_clients[(node_id, "node", session_id, client_id)]

    @check_closed
    @threadsafe
    def attach_configuration_client(self, package_id: str, session_id:str, client_id:str, client_options: dict = {}) -> Client:
        """
        Attach a client instance to a package configuration

        Args:
            package_id: the package configuration to which the client is to be attached
            session_id: the id of an opened interactive session
            client_id: the id of the client to attach
            client_options: optional, a dictionary with extra parameters for the client

        Returns:
             an object which implements the Client API and provides methods to interact with the client
        """
        if session_id not in self.session_ids:
            raise ValueError(f"session {session_id} is not open")
        client = Client()
        execution_client = ExecutionClient(lambda *args: self.__forward_client_message(*args),
                                           package_id, "configuration", session_id, client_id, client, client_options)
        self.execution_clients[(package_id, "configuration", session_id, client_id)] = execution_client
        self.executor.attach_client(package_id, "configuration", session_id, client_id, execution_client)
        return client

    @check_closed
    @threadsafe
    def detach_configuration_client(self, package_id: str, session_id: str, client_id):
        """
        Detach a client instance from a package configuration

        Args:
            package_id: the node to which the client is to be attached
            session_id: the id of an opened interactive session
            client_id: the id of the client to detach
        """
        if (package_id, "configuration", session_id, client_id) in self.execution_clients:
            client = self.execution_clients[(package_id, "configuration", session_id, client_id)]
            self.executor.detach_client(package_id, "configuration", session_id, client_id, client)
            client.close()
            del self.execution_clients[(package_id, "configuration", session_id, client_id)]

    def __handle_client_message(self, target_id, target_type, session_id, client_id, extras):
        if (target_id, target_type, session_id, client_id) in self.execution_clients:
            client = self.execution_clients[(target_id, target_type, session_id, client_id)]
            client.message_callback(*extras)

    @threadsafe
    def __forward_client_message(self, target_id, target_type, session_id, client_id, *msg):
        self.executor.forward_client_message(target_id, target_type, session_id, client_id, *msg)

    @threadsafe
    def __add_node(self, node):
        self.executor.add_node(node)

    @threadsafe
    def __add_link(self, link):
        self.executor.add_link(link)

    @threadsafe
    def __remove_node(self, node):
        self.executor.remove_node(node.get_node_id())

    @threadsafe
    def __remove_link(self, link):
        self.executor.remove_link(link.get_link_id())

    @threadsafe
    def __clear(self):
        self.executor.clear()

    @threadsafe
    def pause(self):
        self.paused = True
        self.executor.pause()

    @check_closed
    @threadsafe
    def resume(self, after_message_delivery:bool=False):
        self.paused = False
        self.executor.resume(after_message_delivery=after_message_delivery)

    @check_closed
    @threadsafe
    def get_engine_pid(self):
        """
        Get the integer process identifier (PID) of the engine sub-process (or None if the engine is not running in a sub-process)

        Returns:
            engine PID
        """
        return self.executor.get_engine_pid()

    @check_closed
    @threadsafe
    def restart(self):
        self.executor.restart()

    def start(self, terminate_on_complete=True, after_message_delivery=True):
        if self.thread is None:
            self.thread = threading.Thread(target=lambda: self.run(terminate_on_complete=terminate_on_complete,
                                                    after_message_delivery=after_message_delivery), daemon=True)
            self.thread.start()

    def join(self):
        self.thread.join()
        self.thread = None

    @check_closed
    def run(self, terminate_on_complete:bool=True, after_message_delivery:bool=True) -> bool:
        """
        Run the execution

        Args:
            terminate_on_complete: if true, terminate the runner as soon as all nodes have finished running
            after_message_delivery: if true, wait for all messages to be delivered to nodes/configurations before running

        Returns:
            True iff the execution resulted in no failed nodes
        """

        try:
            self.lock.acquire()
            self.executor.resume(after_message_delivery)
        finally:
            self.lock.release()
        self.execution_result = self.executor.run(terminate_on_complete=terminate_on_complete)

        return self.execution_result


    def set_close_callback(self, callback):
        self.close_handler = callback

    def get_result(self):
        return self.execution_result

    @threadsafe
    @check_closed
    def stop(self) -> None:
        """
        Stop the current execution, callable from another thread during the execution of run

        Notes:
            the run method will return once any current node executions complete
        """
        if self.executor:
            self.executor.stop()


    @check_closed
    def close(self) -> None:
        """
        Close the runner.  After this call returns, no other methods can be called

        :return:
        """
        if self.executor:
            self.executor.close()
            self.executor = None

        # disconnect listeners from the network
        self.add_node_callback = self.network.unregister_add_node_callback(self.add_node_callback)
        self.add_link_callback = self.network.unregister_add_link_callback(self.add_link_callback)
        self.remove_node_callback = self.network.unregister_remove_node_callback(self.remove_node_callback)
        self.remove_link_callback = self.network.unregister_remove_link_callback(self.remove_link_callback)
        self.clear_network_callback = self.network.unregister_clear_network_callback(
            self.clear_network_callback)

        self.closed = True

        if self.close_handler:
            self.close_handler()


    def __request_open_client(self, origin_id, origin_type, session_id, client_id):
        """
        Pass on a request to open a node or configuration client

        Args:
            origin_id:
            origin_type:
            session_id:
            client_id:

        Returns:

        """
        if self.open_client_request_handler is not None:
            self.open_client_request_handler(origin_id, origin_type, session_id, client_id)
