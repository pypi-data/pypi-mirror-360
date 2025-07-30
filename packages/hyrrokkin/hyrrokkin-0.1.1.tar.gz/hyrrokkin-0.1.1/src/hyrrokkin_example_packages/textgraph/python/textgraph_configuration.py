#   Hyrrokkin - a library for building and running executable graphs
#
#   MIT License - Copyright (C) 2022-2025  Visual Topology Ltd

from hyrrokkin_engine.configuration_interface import ConfigurationInterface

from .text_input_node import TextInputNode
from .word_frequency_node import WordFrequencyNode
from .table_display_node import TableDisplayNode

class TextgraphConfiguration(ConfigurationInterface):

    def __init__(self, services):
        self.services = services

    async def create_node(self, node_type_id, node_services):
        match node_type_id:
            case "text_input_node":
                tin = TextInputNode(node_services)
                await tin.load()
                return tin
            case "word_frequency_node": return WordFrequencyNode(node_services)
            case "table_display_node": return TableDisplayNode(node_services)
            case _: return None





