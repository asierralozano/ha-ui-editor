import os

import yaml

from homeassistant_ui_editor import template as template_
from homeassistant_ui_editor.constants import SETTINGS_THEMES_PATH
from homeassistant_ui_editor.lib.NodeGraphQt import TemplateBaseNode, BaseNode
from homeassistant_ui_editor.settings import HomeAssistantUIEditorSettings

SETTINGS = HomeAssistantUIEditorSettings()


class _HomeAssistantBaseNode(TemplateBaseNode):

    __identifier__ = ""
    EXTRA_WIDTH = 0

    def __init__(self, theme, template_type, template):
        super(_HomeAssistantBaseNode, self).__init__(theme, template_type, template)
        self.view.set_extra_width(self.EXTRA_WIDTH)

    @classmethod
    def node_identifier(cls):
        return f"{cls.__identifier__}.{cls.NODE_NAME}"

    @staticmethod
    def get_template_file(template):
        return os.path.join(SETTINGS.get(SETTINGS_THEMES_PATH), *template.split("."))


class HomeAssistantVisualNode(_HomeAssistantBaseNode):
    @classmethod
    def from_template(cls, template_file):
        # with open(template_file, "w") as tf:
        with open(
            f"{cls.get_template_file(template_file)}.yaml",
            "r",
        ) as tf:
            template_data = yaml.safe_load(tf)

        theme, template_type, template = template_file.split(".")
        instance = cls(theme, template_type, template)
        instance.__identifier__ = template_data.pop("identifier")
        instance.NODE_NAME = template_data.pop("name")
        instance.node_inputs = template_data.get("inputs", dict())
        instance.node_outputs = template_data.get("outputs", dict())
        instance.node_properties = template_data.get("properties", dict())

        instance.init_node()

        return instance

    def __init__(self, theme, template_type, template):
        super(HomeAssistantVisualNode, self).__init__(theme, template_type, template)

        self._node_inputs = dict()
        self._node_outputs = dict()
        self._node_properties = dict()

    def init_node(self):
        self._create_properties()
        self._create_inputs()
        self._create_outputs()

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, template):
        self._template = template

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, theme):
        self._theme = theme

    @property
    def template_type(self):
        return self._template_type

    @template_type.setter
    def template_type(self, template_type):
        self._template_type = template_type

    @property
    def node_inputs(self) -> dict:
        return self._node_inputs

    @node_inputs.setter
    def node_inputs(self, node_inputs):
        self._node_inputs = node_inputs

    @property
    def node_outputs(self) -> dict:
        return self._node_outputs

    @node_outputs.setter
    def node_outputs(self, node_outputs):
        self._node_outputs = node_outputs

    @property
    def node_properties(self) -> dict:
        return self._node_properties

    @node_properties.setter
    def node_properties(self, node_properties):
        self._node_properties = node_properties

    def _create_properties(self):
        for property, property_values in self.node_properties.items():
            self.add_input(name=property, color=(233, 45, 56), **property_values)

    def _create_inputs(self):
        for input, input_values in self.node_inputs.items():
            self.add_input(name=input, **input_values)

    def _create_outputs(self):
        for output, output_values in self.node_outputs.items():
            self.add_output(name=output, **output_values)

    def get_context(self):
        context = {"cards": []}
        for port, nodes in self.connected_input_nodes().items():
            if not nodes:
                continue
            for node in nodes:
                if issubclass(node.__class__, HomeAssistantTypeNode):
                    context[port.name()] = node.get_value()
                elif issubclass(node.__class__, HomeAssistantVisualNode):
                    context["cards"].append(node.run())
                else:
                    continue
        return context

    def run(self):
        context = self.get_context()
        return template_._render_jinja(
            f"{self.template}.j2", self.theme, self.template_type, **context
        )


class HomeAssistantTypeNode(BaseNode):

    __identifier__ = "type"

    def __init__(self):
        super(HomeAssistantTypeNode, self).__init__()

        self.add_output("out", limited_type=self.property_type())

    def node_property(self) -> str:
        return "widget_value"

    def property_type(self):
        return "str"

    def get_value(self):
        return self.get_property(self.node_property())
