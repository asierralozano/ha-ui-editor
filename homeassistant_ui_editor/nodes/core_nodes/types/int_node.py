from homeassistant_ui_editor.nodes.core_nodes.node_base import HomeAssistantTypeNode


class IntNode(HomeAssistantTypeNode):

    NODE_NAME = "Int"

    def __init__(self):
        super(IntNode, self).__init__()
        self.add_int_input(self.node_property())

    def node_property(self):
        return "Int"

    def property_type(self):
        return "int"
