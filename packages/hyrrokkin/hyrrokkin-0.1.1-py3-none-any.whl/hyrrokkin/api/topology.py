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

import io
import os
import logging
from typing import Union, Dict, List, Callable, Any

JsonType = Union[Dict[str, "JsonType"], List["JsonType"], str, int, float, bool, None]


from hyrrokkin.schema.schema import Schema
from hyrrokkin.model.node import Node
from hyrrokkin.model.link import Link
from hyrrokkin.exceptions.invalid_link_error import InvalidLinkError
from hyrrokkin.exceptions.invalid_node_error import InvalidNodeError


from hyrrokkin.model.network import Network
from hyrrokkin.api.topology_runner import TopologyRunner
from hyrrokkin.engine_launchers.engine_launcher import EngineLauncher

def check_not_running(func):
    """
    Decorator that prevents access to a method if any runners are running
    :param func: the method to be decorated
    :return: wrapped method
    """
    def threadsafe_wrapper(self, *args, **kwargs):
        if len(self.read_only_runners) > 0 or len(self.read_write_runners) > 0:
            pass # raise Exception("Runners are active")
        return func(self, *args, **kwargs)
    return threadsafe_wrapper

class Topology:


    def __init__(self, execution_folder:str, package_list: list[str]):
        """
        Create a topology

        Args:
            execution_folder: the folder used to store the topology definition and files
            package_list: a list of the paths to python packages containing schemas (a schema.json)


        """
        self.execution_folder = execution_folder

        self.logger = logging.getLogger("topology")

        if self.execution_folder:
            os.makedirs(self.execution_folder, exist_ok=True)

        self.schema = Schema()
        for package in package_list:
            self.schema.load_package(package)

        self.network = Network(self.schema, self.execution_folder)

        # the empty flag indicates that the topology contains no nodes and no
        # package properties or package data has been assigned
        self.empty = True

        # track which runners have been opened and are not yet closed
        self.read_only_runners = set()
        self.read_write_runners = set() # at most 1

    def load_zip(self, from_file: io.BytesIO) -> dict:
        """
        Load a topology from a binary stream

        Args:
            from_file: a binary stream, opened for reading

        Returns:
            a dictionary containing any node renamings performed to avoid id collisions with existing nodes
        """
        (added_node_ids, added_link_ids, node_renamings) = self.network.load_zip(from_file, merging=not self.empty)
        self.empty = False
        return node_renamings

    def load_dir(self):
        """
        Load a topology from the execution folder
        """
        (added_node_ids, added_link_ids, node_renamings) = self.network.load_dir({})
        self.empty = False

    def save_zip(self, to_file: io.BufferedWriter=None, include_data:bool=True) ->Union[None,bytes]:
        """
        Save a topology to a binary stream

        Args:
            to_file: an opened binary file to which the topology will be saved, if provided
            include_data: whether to include node/configuration data in the saved zip

        Returns:
            if to_file is not provided, returns a bytes object containing the saved topology
        """
        return self.network.save_zip(to_file, include_data=include_data)

    def open_runner(self, status_event_handler: Callable[[str, str, str, str], None] = None,
                 execution_event_handler: Callable[[Union[float,None], str, str, Union[Dict, Exception, None], bool], None] = None,
                 engine_launcher: Union[EngineLauncher,None]=None,
                 read_only: bool = False) -> TopologyRunner:
        """
        Create a runner to run the topology

        Args:
            status_event_handler: specify a function to call when a node/configuration sets its status
                                 passing parameters target_id, target_type, msg, status
            execution_event_handler: specify a function to call when a node changes its execution status
                                passing parameters timestamp, node_id, state, exception, is_manual
            engine_launcher: the engine_launcher to use to run the topology in a remote process.  if not specified, select an appropriate one
                             for the packages loaded
            read_only: if true, do not allow nodes and configurations to persist data/properties changes to disk when running the topology

        Returns: a TopologyInteractor instance that allows the execution to be stopped and clients to be attached and detached
        """
        if not read_only:
            if not self.execution_folder:
                raise ValueError("An execution folder must be associated with this topology for it to be run with read_only set to False")

        if len(self.read_write_runners) > 0:
            raise ValueError("An open runner with read-write access exists")

        if not read_only:
            if len(self.read_only_runners) > 0:
                raise ValueError("Open runner(s) with read-only access exists")

        runner = TopologyRunner(network=self.network, schema=self.schema, execution_folder=self.execution_folder,
                                         engine_launcher=engine_launcher, status_event_handler=status_event_handler,
                                         execution_event_handler=execution_event_handler, read_only=read_only)

        if read_only:
            self.read_only_runners.add(runner)
            runner.set_close_callback(lambda: self.read_only_runners.remove(runner))
        else:
            self.read_write_runners.add(runner)
            runner.set_close_callback(lambda: self.read_write_runners.remove(runner))

        return runner

    def set_metadata(self, metadata: dict[str, str]):
        """
        Set metadata for this topology

        Args:
            metadata: a dictionary containing metadata, consisting of string keys and values.

        Notes:
            the following keys will be understood by hyrrokkin based tools - version, description, authors
        """
        self.network.set_metadata(metadata)

    def add_node(self, node_id: str, node_type: str, properties: dict[str, JsonType]={},
                 metadata:dict[str, JsonType]={}, x:int=0, y:int=0) -> str:
        """
        Add a node to the topology

        Args:
            node_id: the node's unique identifier, must not already exist within the topology
            node_type: the type of the node, a string of the form package_id:node_type_id
            properties: dictionary containing the node's property names and values, must be JSON serialisable
            metadata: a dictionary containing the new metadata
            x: the new x-coordinate value
            y: the new y-coordinate value
        """
        if self.network.get_node(node_id) is not None:
            raise InvalidNodeError(f"Node with id {node_id} already exists")

        node = Node(node_id, node_type, x=x, y=y, metadata=metadata)
        self.network.add_node(node)
        dsu = self.network.get_node_datastore(node_id)
        dsu.set_properties(properties)
        self.empty = False
        return node_id

    def remove_node(self, node_id: str):
        """
        Remove a node from the topology

        Args:
            node_id: the node's unique identifier
        """
        if self.network.get_node(node_id) is None:
            raise InvalidNodeError(f"Node with id {node_id} does not exist")
        self.network.remove_node(node_id)

    def update_node_position(self, node_id:str, x:int, y:int):
        """
        Update a node's position

        Args:
            node_id: the id of the node to update
            x: the new x-coordinate value
            y: the new y-coordinate value
        """
        self.network.move_node(node_id, x, y)

    @check_not_running
    def get_node_properties(self, node_id: str) -> dict[str,JsonType]:
        """
        Gets the properties of a node

        Args:
            node_id: the node's identifier

        Returns:
            dictionary containing properties
        """
        dsu = self.network.get_node_datastore(node_id)
        return dsu.get_properties()

    @check_not_running
    def set_node_properties(self, node_id: str, properties:dict[str,JsonType]):
        """
        Update the property of a node

        Args:
            node_id: the node's identifier
            properties: dictionary containing properties
        """
        dsu = self.network.get_node_datastore(node_id)
        dsu.set_properties(properties)

    @check_not_running
    def get_node_data(self, node_id: str, key: str) -> Union[bytes, None]:
        """
        Get binary data associated with this node.

        Args:
            node_id: node identifier
            key: a key to locate the data (can only contain alphanumeric characters and underscores)

        Returns:
            data or None if no data is associated with the key
        """
        dsu = self.network.get_node_datastore(node_id)
        return dsu.get_data(key)

    @check_not_running
    def set_node_data(self, node_id: str, key: str, data: Union[bytes,None]):
        """
        Set binary data associated with this node.

        Args:
            node_id: node identifier
            key: a key to locate the data (can only contain alphanumeric characters and underscores)
            data: data to be stored
        """
        dsu = self.network.get_node_datastore(node_id)
        dsu.set_data(key, data)

    @check_not_running
    def get_node_data_keys(self, node_id:str) -> list[str]:
        """
        Get the list of keys for which the node stores binary data

        Args:
            node_id: node identifier

        Returns:
            a set of data keys
        """
        dsu = self.network.get_node_datastore(node_id)
        return dsu.get_data_keys()

    @check_not_running
    def get_configuration_properties(self, package_id: str) -> dict[str,JsonType]:
        """
        Gets the properties package configuration

        Args:
            package_id: the package's identifier

        Returns:
            dictionary containing properties
        """
        dsu = self.network.get_configuration_datastore(package_id)
        return dsu.get_properties()

    @check_not_running
    def set_configuration_property(self, package_id: str, properties:dict[str,JsonType]):
        """
        Update a property of a package configuration

        Args:
            package_id: the package's identifier
            properties: dictionary containing properties
        """
        dsu = self.network.get_configuration_datastore(package_id)
        dsu.set_properties(properties)
        self.empty = False

    @check_not_running
    def set_configuration_properties(self, package_id: str, properties: dict):
        """
        Set the properties of a package's configuration

        Args:
            package_id: the id of the packahe
            properties: a dictionary containing the configuration properties, must be JSON serialisable.
        """
        dsu = self.network.get_configuration_datastore(package_id)
        dsu.set_properties(properties)
        self.empty = False

    @check_not_running
    def get_configuration_data(self, package_id: str, key: str) -> Union[bytes, str, None]:
        """
        Get binary or string data associated with a package configuration.

        Args:
            package_id: package identifier
            key: a key to locate the data (can only contain alphanumeric characters and underscores)

        Returns:
            data or None if no data is associated with the key
        """
        dsu = self.network.get_configuration_datastore(package_id)
        return dsu.get_data(key)

    @check_not_running
    def set_configuration_data(self, package_id: str, key: str, data: Union[bytes, str, None]):
        """
        Set binary or string data associated with this node.

        Args:
            package_id: package identifier
            key: a key to locate the data (can only contain alphanumeric characters and underscores)
            data: data to be stored
        """
        dsu = self.network.get_configuration_datastore(package_id)
        dsu.set_data(key, data)
        self.empty = False

    @check_not_running
    def get_configuration_data_keys(self, package_id: str) -> list[str]:
        """
        Get the list of keys for which the package configuration stores binary data

        Args:
            package_id: package identifier

        Returns:
            a set of data keys
        """
        dsu = self.network.get_configuration_datastore(package_id)
        return dsu.get_data_keys()

    def add_link(self, link_id: str, from_node_id: str, from_port: Union[str, None], to_node_id: str,
                 to_port: Union[str, None]):
        """
        Add a link to the topology

        Args:
            link_id: a unique identifier for the link
            from_node_id: node id of the source node
            from_port: port name on the source node, can be omitted if the "from" node has only one output port
            to_node_id: node id of the destination node
            to_port: port name on the destination node, can be ommitted if the "to" node has only one input port

        Raises:
            InvalidLinkError: if the link cannot be added
        """

        if self.network.get_link(link_id) is not None:
            raise InvalidLinkError(f"Link with id {link_id} already exists")

        from_node = self.network.get_node(from_node_id)
        if from_node is None:
            raise InvalidLinkError(f"{from_node_id} does not exist")

        from_node_type_name = from_node.get_node_type()
        from_node_type = self.schema.get_node_type(from_node_type_name)

        to_node = self.network.get_node(to_node_id)
        if to_node is None:
            raise InvalidLinkError(f"{to_node_id} does not exist")
        to_node_type_name = to_node.get_node_type()
        to_node_type = self.schema.get_node_type(to_node_type_name)

        if from_port is None:
            if len(from_node_type.output_ports) == 1:
                from_port = next(iter(from_node_type.output_ports))
            else:
                output_port_names = ",".join(list(from_node_type.output_ports.keys()))
                raise InvalidLinkError(f"from_port not specified for link, should be one of ({output_port_names})")
        else:
            if from_port not in from_node_type.output_ports:
                raise InvalidLinkError(f"{from_port} is not a valid output port for node {from_node_id}")

        if to_port is None:
            if len(to_node_type.input_ports) == 1:
                to_port = next(iter(to_node_type.input_ports))
            else:
                input_port_names = ",".join(list(to_node_type.input_ports.keys()))
                raise InvalidLinkError(f"to_port not specified for link, should be one of ({input_port_names})")
        else:
            if to_port not in to_node_type.input_ports:
                raise InvalidLinkError(f"{to_port} is not a valid output port for node {to_node_id}")

        from_link_type = from_node_type.output_ports[from_port].link_type

        to_link_type = to_node_type.input_ports[to_port].link_type

        if from_link_type != to_link_type:
            raise InvalidLinkError(f"incompatible link types (from: {from_link_type}, to: {to_link_type})")

        if not from_node_type.output_ports[from_port].allows_multiple_connections():
            if len(self.network.get_outputs_from(from_node_id, from_port)) > 0:
                raise InvalidLinkError(
                    f"output port {from_node_id}/{from_port} is already connected and does not allow multiple connections")

        if not to_node_type.input_ports[to_port].allows_multiple_connections():
            if len(self.network.get_inputs_to(to_node_id, to_port)) > 0:
                raise InvalidLinkError(
                    f"input port {to_node_id}/{to_port} is already connected and does not allow multiple connections")

        link = Link(link_id, from_node_id, from_port, to_node_id, to_port, from_link_type)
        self.network.add_link(link)

    def remove_link(self, link_id: str):
        """
        Remove a link from the topology

        Args:
            link_id: the link's unique identifier
        """
        if self.network.get_link(link_id) is None:
            raise InvalidNodeError(f"Link with id {link_id} does not exist")
        else:
            self.network.remove_link(link_id)

    def get_package_ids(self) -> list[str]:
        """
        Gets the ids of all packages

        Returns:
             list of package ids
        """
        return list(self.schema.get_packages().keys())

    def get_node_ids(self) -> list[str]:
        """
        Get the ids of all nodes in the topology

        Returns:
            list of node ids
        """
        return self.network.get_node_ids()

    def get_node_type(self, node_id: str) -> tuple[str, str]:
        """
        Get the node package and type for a given node

        Args:
            node_id: the id of the node to retrieve

        Returns:
            tuple (package_id, node_type_id)
        """
        node = self.network.get_node(node_id)
        node_type = node.get_node_type()
        return self.schema.split_descriptor(node_type)

    def serialise_node(self, node_id:str) -> dict[str, JsonType]:
        """
        Serialise a node to a dictionary with self-explanatory keys

        Args:
            node_id: the id of the node to serialise

        Returns:
            a dictionary describing the node
        """
        node = self.network.get_node(node_id)
        d = {}
        d["node_id"] = node_id
        d["node_type"] = node.get_node_type()
        (x, y) = node.get_xy()
        d["x"] = x
        d["y"] = y
        d["metadata"] = node.get_metadata()
        return d

    def serialise_link(self, link_id:str) -> dict[str, JsonType]:
        """
        Serialise a link to a dictionary with self-explanatory keys

        Args:
            link_id: the id of the link to serialise

        Returns:
            a dictionary describing the link
        """
        link = self.network.get_link(link_id)
        msg = {}
        msg["link_id"] = link_id
        msg["link_type"] = link.get_link_type()
        msg["from_node"] = link.from_node_id
        msg["from_port"] = link.from_port
        msg["to_node"] = link.to_node_id
        msg["to_port"] = link.to_port
        return msg

    def serialise(self) -> dict[str,JsonType]:
        """
        Serialise the topology to a dictionary without data/properties

        Returns:
            a dictionary describing the topoology
        """

        return self.network.save()

    def get_node_metadata(self, node_id: str) -> dict[str, JsonType]:
        """
        Get the metadata of a node

        Args:
            node_id: the id of the node

        Returns:
            A dictionary containing the metadata
        """
        return self.network.get_node(node_id).get_metadata()

    def update_node_metadata(self, node_id:str, metadata:dict[str,JsonType]):
        """
        Updates the metadata of a node

        Args:
            node_id: the id of the node
            metadata: a dictionary containing the new metadata
        """
        node = self.network.get_node(node_id)
        node.update_metadata(metadata)

    def get_link_ids(self) -> list[str]:
        """
        Get the ids of all links in the topology

        Returns:
            list of link ids
        """
        return self.network.get_link_ids()

    def get_link(self, link_id:str) -> tuple[str, str, str, str]:
        """
        Get the link details for a given link

        Args:
            link_id: the id of the link to retrieve

        Returns:
            tuple (from_node_id,from_port,to_node_id,to_port)
        """
        link = self.network.get_link(link_id)
        return (link.from_node_id, link.from_port, link.to_node_id, link.to_port)

    def get_output_port_names(self, node_id: str) -> list[str]:
        """
        Get the output port names for a given node

        Args:
            node_id: the id of the node

        Returns:
            list of output port names
        """
        node = self.network.get_node(node_id)
        node_type = self.schema.get_node_type(node.get_node_type())
        return [name for (name, _) in node_type.get_output_ports()]

    def get_input_port_names(self, node_id: str) -> list[str]:
        """
        Get the input port names for a given node

        Args:
            node_id: the id of the node

        Returns:
            list of input port names
        """
        node = self.network.get_node(node_id)
        node_type = self.schema.get_node_type(node.get_node_type())
        return [name for (name, _) in node_type.get_input_ports()]

    def get_metadata(self) -> dict[str, JsonType]:
        """
        Get the metadata of the topology

        Returns:
            A dictionary containing the metadata
        """
        return self.network.get_metadata()

    @check_not_running
    def get_node_properties(self, node_id: str) -> dict[str, JsonType]:
        """
        Get the properties for the specified node

        Args:
            node_id: the node identifier

        Returns:
            A dictionary containing the properties defined for that node
        """
        dsu = self.network.get_node_datastore(node_id)
        return dsu.get_properties()

    @check_not_running
    def get_configuration_properties(self, package_id: str) -> dict[str, JsonType]:
        """
        Get the properties for the specified package configuration

        Args:
            package_id: the package identifier

        Returns:
            A dictionary containing the properties defined for that package configuration
        """
        dsu = self.network.get_configuration_datastore(package_id)
        return dsu.get_properties()

    def clear(self):
        """
        Remove all nodes and links from the topology
        """
        self.network.clear()

