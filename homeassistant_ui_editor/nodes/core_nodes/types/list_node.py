from homeassistant_ui_editor.nodes.core_nodes.node_base import HomeAssistantTypeNode


class ListNode(HomeAssistantTypeNode):

    NODE_NAME = "List"

    def __init__(self, items):
        super(ListNode, self).__init__()
        self.add_combo_menu(self.node_property(), items=items)

    def property_type(self):
        return "str"


class SVGIconsNode(ListNode):

    NODE_NAME = "Icons"

    def __init__(self):
        items = ["asdasd", "asdasdasda"]
        super(SVGIconsNode, self).__init__(items)

    def property_type(self):
        return "dict"
