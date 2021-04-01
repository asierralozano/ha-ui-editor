from PySide2 import QtWidgets, QtCore, QtGui


class HomeAssistantUIPropertiesTab(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(HomeAssistantUIPropertiesTab, self).__init__(parent=parent)

        self._selected_node = None
        self._main_layout = QtWidgets.QVBoxLayout()
        self._properties_scroll_area = QtWidgets.QScrollArea()
        self._properties_scroll_area.setWidgetResizable(True)

        self._init_ui()

    def _init_ui(self):
        self._main_layout.addWidget(self._properties_scroll_area)
        self.setLayout(self._main_layout)

    def node_doubled_clicked(self, node):
        self._selected_node = node
        self._clear_scroll_area()
        self._create_node_widget(node)

    def _clear_scroll_area(self):
        self._properties_scroll_area.takeWidget()

    def _create_node_widget(self, node):
        node_widget = QtWidgets.QWidget()
        node_layout = QtWidgets.QVBoxLayout(node_widget)

        for property_name, property_attributes in node.node_properties.items():
            property_widget = QtWidgets.QWidget()
            property_layout = QtWidgets.QVBoxLayout(property_widget)

            property_type = property_attributes.get("limited_type", "str")
            label = QtWidgets.QLabel(property_name.capitalize())

            property_value = node.get_property(property_name)
            widget_value = property_value if property_value else property_attributes.get("default", "")

            if property_type == "str":
                widget = QtWidgets.QLineEdit()
                widget.setText(widget_value)
                widget.textChanged.connect(self._set_value_to_node)

            elif property_type == "int":
                widget = QtWidgets.QSpinBox()
                widget.setValue(int(widget_value))
                widget.valueChanged.connect(self._set_value_to_node)

            elif property_type == "bool":
                widget = QtWidgets.QCheckBox()
                widget.setChecked(bool(widget_value))
                widget.stateChanged.connect(self._set_value_to_node)

            else:
                widget = QtWidgets.QLineEdit()
                widget.setText(str(node.get_property(property_name)))
                widget.textChanged.connect(self._set_value_to_node)

            widget.property_name = property_name
            widget.property_type = property_type

            property_layout.addWidget(label)
            property_layout.addWidget(widget)

            node_layout.addWidget(property_widget)

        node_layout.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self._properties_scroll_area.setWidget(node_widget)

    def _set_value_to_node(self, value):
        if self.sender().property_type == "bool":
            value = bool(value)
            # print(value)
        self._selected_node.set_property(self.sender().property_name, value)
