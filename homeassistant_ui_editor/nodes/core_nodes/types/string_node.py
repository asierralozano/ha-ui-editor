from homeassistant_ui_editor.nodes.core_nodes.node_base import HomeAssistantTypeNode


class StringNode(HomeAssistantTypeNode):

    NODE_NAME = "String"

    def __init__(self):
        super(StringNode, self).__init__()
        self.add_text_input(self.node_property())

    def property_type(self):
        return "str"


class LongStringNode(HomeAssistantTypeNode):

    NODE_NAME = "LongString"

    def __init__(self):
        super(LongStringNode, self).__init__()
        self.add_long_text_input(self.node_property())

    def property_type(self):
        return "str"

