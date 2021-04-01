from PySide2 import QtWidgets, QtCore, QtGui
from .graph import HomeAssistantUIEditorGraph
from .properties import HomeAssistantUIPropertiesTab
from .nodes.core_nodes.node_base import HomeAssistantVisualNode
from .ui.code_editor import QCodeEditor


class HomeAssistantUIEditorWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(HomeAssistantUIEditorWindow, self).__init__()

        self._selected_node = None
        self._graph = HomeAssistantUIEditorGraph()
        self._properties_tab = HomeAssistantUIPropertiesTab()
        self._code_editor = QCodeEditor()

        properties_dock_widget = QtWidgets.QDockWidget("Properties")
        properties_dock_widget.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
        )
        properties_dock_widget.setWidget(self._properties_tab)

        self.setCentralWidget(self._graph.widget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, properties_dock_widget)

        code_editor = QtWidgets.QDockWidget("Editor")
        code_editor.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable
            | QtWidgets.QDockWidget.DockWidgetFloatable
        )
        code_editor.setWidget(self._code_editor)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, code_editor)

        self._connect_signals()

    def _connect_signals(self):
        self.graph.node_double_clicked.connect(self._node_double_clicked)
        self.graph.property_changed.connect(self._property_changed)
        self.graph.port_connected.connect(self._port_connected)

    def _node_double_clicked(self, node):
        if isinstance(node, HomeAssistantVisualNode):
            self._properties_tab.node_doubled_clicked(node)
            self._code_editor.clear()
            code = node.run()
            self._code_editor.setPlainText(code)

            self._selected_node = node

    def _property_changed(self, node, property, __):
        if property in node.node_properties:
            code = node.run()
            self._code_editor.setPlainText(code)

    def _port_connected(self, input_port, output_port):
        if input_port.node() == self._selected_node:
            code = input_port.node().run()
            self._code_editor.setPlainText(code)

    @property
    def graph(self):
        return self._graph
