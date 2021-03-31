import sys

from NodeGraphQt import QtWidgets
from NodeGraphQt import NodeGraph, BaseNode, setup_context_menu
from homeassistant_ui_editor.nodes.view import ViewNode

# create a example node object with a input/output port.
class MyNode(BaseNode):
    """example test node."""

    # unique node identifier domain. ("com.chantasticvfx.MyNode")
    __identifier__ = 'com.chantasticvfx'

    # initial default node name.
    NODE_NAME = 'My Node'

    def __init__(self):
        super(MyNode, self).__init__()
        self.add_input('foo', color=(180, 80, 0))
        self.add_output('bar')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # create the node graph controller.
    graph = NodeGraph()
    # set up default menu and commands.
    setup_context_menu(graph)

    # register backdrop node. (included in the NodeGraphQt module)
    # graph.register_node(BackdropNode)

    # register example node into the node graph.
    graph.register_node(ViewNode)
    print(graph.registered_nodes())

    # create nodes.
    # backdrop = graph.create_node('nodeGraphQt.nodes.Backdrop', name='Backdrop')
    node_a = graph.create_node(ViewNode.node_identifier(), name='Main View')
    # node_b = graph.create_node(ViewNode.node_identifier(), name='Node B', color='#5b162f')

    # connect node a input to node b output.
    # node_a.set_input(0, node_b.output(0))

    # get the widget and show.
    graph_widget = graph.widget
    graph_widget.show()


    app.exec_()

# import sys
# from PySide2 import QtWidgets
#
# app = QtWidgets.QApplication()
# bt = QtWidgets.QPushButton("aaa")
# bt.show()
# sys.exit(app.exec_())