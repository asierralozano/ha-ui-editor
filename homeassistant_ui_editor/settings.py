import typing
from PySide2 import QtCore, QtGui, QtWidgets
from homeassistant_ui_editor.constants import SETTINGS_NAME_MAPPING


class HomeAssistantUIEditorSettings(QtCore.QObject):

    org = "ASierraLozano"
    app_name = "LovelaceCustomEditor"

    def __init__(self):
        super().__init__()
        self._settings = QtCore.QSettings(self.org, self.app_name)

    @property
    def settings(self):
        return self._settings

    def set(self, key, value, group=None) -> typing.NoReturn:
        if group:
            self.settings.beginGroup(group)
        self.settings.setValue(key, value)
        if group:
            self.settings.endGroup()

    def get(self, key, group=None) -> typing.Any:
        if group:
            self.settings.beginGroup(group)
        value = self.settings.value(key)
        if group:
            self.settings.endGroup()
        return value

    def remove(self, key, group=None) -> typing.NoReturn:
        if group:
            self.settings.beginGroup(group)
        self.settings.remove(key)
        if group:
            self.settings.endGroup()

    def exists(self, key) -> bool:
        return key in self.all()

    def all(self) -> list:
        return self.settings.allKeys()


class HomeAssistantUIEditorDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(HomeAssistantUIEditorDialog, self).__init__(parent=parent)

        self._settings = HomeAssistantUIEditorSettings()
        self._main_layout = QtWidgets.QVBoxLayout()
        self._main_settings_layout = QtWidgets.QFormLayout()

        self._main_layout.addLayout(self._main_settings_layout)

        self.setLayout(self._main_layout)

        self._widgets_data = list()

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Preferences")
        self._create_settings_widgets()
        self._create_buttons()

    def _create_settings_widgets(self):
        for key in self._settings.all():
            value = self._settings.get(key)
            if isinstance(value, str):
                widget = QtWidgets.QLineEdit()
                widget.setMinimumWidth(300)
                widget.setText(value)
            else:
                continue

            beauty_name = SETTINGS_NAME_MAPPING.get(key)
            self._widgets_data.append(
                {
                    "setting_name": key,
                    "beauty_name": beauty_name,
                    "widget": widget,
                    "getter": "text"
                }
            )
            self._main_settings_layout.addRow(beauty_name, widget)

    def _save_settings(self):
        for widget_data in self._widgets_data:
            setting_name = widget_data.get("setting_name")
            widget = widget_data.get("widget")
            getter_fn = getattr(widget, widget_data.get("getter"))
            widget_value = getter_fn()

            self._settings.set(setting_name, widget_value)

    def _create_buttons(self):
        buttons_layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(self.save)

        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        self._main_layout.addLayout(buttons_layout)

    def save(self):
        self._save_settings()
        self.accept()


if __name__ == '__main__':
    # ha_settings = HomeAssistantUIEditorSettings()
    # ha_settings.remove("path", "themes")
    # # ha_settings.set("themes/path", "asdasdasdas")
    # print(ha_settings.all())
    import sys
    app = QtWidgets.QApplication(sys.argv)

    dialog = HomeAssistantUIEditorDialog()
    dialog.exec_()
    # app.exec_()