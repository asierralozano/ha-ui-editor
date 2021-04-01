import os
import sys

from Qt import QtWidgets

from homeassistant_ui_editor.constants import SETTINGS_THEMES_PATH
# from homeassistant_ui_editor.graph import HomeAssistantUIEditorGraph
from homeassistant_ui_editor.editor import HomeAssistantUIEditorWindow
from homeassistant_ui_editor.register import register
from homeassistant_ui_editor.settings import HomeAssistantUIEditorSettings

SETTINGS = HomeAssistantUIEditorSettings()


def _themes_path_setting_exists():
    theme_path_exists = SETTINGS.exists(SETTINGS_THEMES_PATH)
    if not theme_path_exists:
        return False
    themes_path = SETTINGS.get(SETTINGS_THEMES_PATH)
    if not os.path.isdir(themes_path):
        return False
    return True


def start():
    app = QtWidgets.QApplication(sys.argv)

    themes_path_exists = _themes_path_setting_exists()
    if not themes_path_exists:
        msg = "It looks like is your first time executing this tool. You have to set " \
              "the path where you are going to save all the incoming themes\n" \
              "Thanks for using the tool!"
        themes_path, accepted = QtWidgets.QInputDialog.getText(None, "Lovelace Custom Editor", msg)
        if not accepted:
            return
        SETTINGS.set(SETTINGS_THEMES_PATH, themes_path)

    editor = HomeAssistantUIEditorWindow()
    editor.resize(1400, 700)

    register(editor.graph)

    # graph_widget = graph.widget
    # graph_widget.show()
    editor.show()

    app.exec_()


if __name__ == '__main__':
    start()