from homeassistant_ui_editor.lib.NodeGraphQt import BaseNode
from homeassistant_ui_editor.nodes.core_nodes.node_base import HomeAssistantTypeNode, HomeAssistantVisualNode


class HomeAssistantOutputNode(BaseNode):

    __identifier__ = "utility"
    NODE_NAME = "Output"

    def __init__(self):
        super(HomeAssistantOutputNode, self).__init__()

        self.add_input("input")
        self.add_long_text_input("output")

    def on_input_connected(self, in_port, out_port):
        out_node = out_port.node()
        widget = self.get_widget("output")
        if isinstance(out_node, HomeAssistantTypeNode):
            widget.set_value(str(out_node.get_value()))
        elif isinstance(out_node, HomeAssistantVisualNode):
            widget.set_value(str(out_node.run()))


