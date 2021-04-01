import os

from homeassistant_ui_editor.lib.NodeGraphQt import NodeGraph, BackdropNode
from homeassistant_ui_editor.nodes import (
    IntNode,
    StringNode,
    BoolNode,
    SVGIconsNode,
    LongStringNode,
    HomeAssistantOutputNode,
)
from homeassistant_ui_editor.nodes.core_nodes.node_base import HomeAssistantVisualNode
from .constants import SETTINGS_THEMES_PATH
from .settings import HomeAssistantUIEditorSettings
from .theme_manager import ThemeManager

SETTINGS = HomeAssistantUIEditorSettings()


def register(graph: NodeGraph):

    try:
        theme_manager = ThemeManager()
        theme_manager.load()

        for template in theme_manager.cards():
            graph.register_node_from_template(template, HomeAssistantVisualNode)
    except:
        pass

    # Types
    # graph.register_node(StringNode)
    # graph.register_node(LongStringNode)
    # graph.register_node(IntNode)
    # graph.register_node(BoolNode)
    # graph.register_node(SVGIconsNode)

    # Utility
    graph.register_node(BackdropNode)
    # graph.register_node(HomeAssistantOutputNode)
    # graph.register_node(SubGraphNode)
    # graph.register_node(SubGraphInputNode)
    # graph.register_node(SubGraphOutputNode)


def _register_themes():
    themes_path = SETTINGS.get(SETTINGS_THEMES_PATH)
    templates = list()
    for theme in os.listdir(themes_path):
        for theme_type in os.listdir(os.path.join(themes_path, theme)):
            for template in os.listdir(os.path.join(themes_path, theme, theme_type)):
                if os.path.isdir(
                    os.path.join(themes_path, theme, theme_type, template)
                ):
                    continue
                templates.append(
                    f"{theme}.{theme_type}.{os.path.splitext(template)[0]}"
                )
    return templates
