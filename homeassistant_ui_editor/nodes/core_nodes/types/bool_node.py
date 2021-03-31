from homeassistant_ui_editor.nodes.core_nodes.node_base import HomeAssistantTypeNode


class BoolNode(HomeAssistantTypeNode):

    NODE_NAME = "Bool"

    def __init__(self):
        super(BoolNode, self).__init__()
        self.add_checkbox(self.node_property())

    def property_type(self):
        return "bool"
