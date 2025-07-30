#   Hyrrokkin - a library for building and running executable graphs
#
#   MIT License - Copyright (C) 2022-2025  Visual Topology Ltd

import json

from hyrrokkin_engine.node_interface import NodeInterface

class TableDisplayNode(NodeInterface):

    def __init__(self, services):
        self.services = services
        self.clients = set()
        self.input_value = None

    async def reset_run(self):
        self.input_value = None
        for client in self.clients:
            client.send_message(self.input_value)

    async def run(self, inputs):
        self.input_value = None
        if "data_in" in inputs:
            self.input_value = inputs["data_in"]
            self.services.set_status(f"{len(self.input_value) - 1} rows", "info")
        else:
            self.services.set_status("No data", "warning")
        for client in self.clients:
            client.send_message(self.input_value)

    async def open_client(self, client):
        self.clients.add(client)
        client.send_message(self.input_value)

    async def close_client(self, client):
        self.clients.remove(client)



