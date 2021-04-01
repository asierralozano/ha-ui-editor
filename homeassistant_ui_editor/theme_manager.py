import os
import yaml

import typing

from homeassistant_ui_editor.settings import HomeAssistantUIEditorSettings
from homeassistant_ui_editor.constants import (
    SETTINGS_THEMES_PATH,
    THEME_SPEC_FILE_NAME,
    CARDS_EXTENSION,
)


class Theme(object):
    def __init__(self, theme_path, specs: str):
        self._theme_path = theme_path
        self._specs = self.load_spec(specs)

    @property
    def theme_path(self) -> str:
        return self._theme_path

    @property
    def specs(self) -> dict:
        return self._specs

    @property
    def name(self):
        return self.get_spec("identifier")

    @property
    def card_types(self):
        card_types = list()
        for _file in os.listdir(self.theme_path):
            if (
                os.path.isfile(os.path.join(self.theme_path, _file))
                or _file == "ha-resources"
            ):
                continue
            card_types.append(_file)
        return card_types

    @property
    def cards(self):
        cards = list()
        for card_type in self.card_types:
            for card in os.listdir(os.path.join(self.theme_path, card_type)):
                card_name, extension = os.path.splitext(card)
                if extension == CARDS_EXTENSION:
                    cards.append(f"{self.name}.{card_type}.{card_name}")
        return cards

    @staticmethod
    def load_spec(spec_file) -> dict:
        with open(spec_file) as sf:
            data = yaml.safe_load(sf)
        return data

    def get_spec(self, key) -> typing.Any:
        return self._specs.get(key)

    def get_template(self, template_type, template_name):
        return os.path.join(self.theme_path, template_type, template_name)


class ThemeManager(object):

    _loaded_themes = list()

    def __init__(self, themes_path=None):
        self._settings = HomeAssistantUIEditorSettings()
        if not themes_path:
            themes_path = self._settings.get(SETTINGS_THEMES_PATH)
        self._themes_path = themes_path

    @property
    def themes_path(self) -> str:
        return self._themes_path

    @property
    def loaded_themes(self) -> typing.List[typing.Optional[Theme]]:
        return self._loaded_themes

    def list_themes(self, include_spec=False):
        themes = list()
        for theme in os.listdir(self.themes_path):
            spec_file = os.path.join(self.themes_path, theme, THEME_SPEC_FILE_NAME)
            if os.path.isfile(
                spec_file
            ):
                spec_data = Theme.load_spec(spec_file)
                theme_name = spec_data.get("identifier")
                if include_spec:
                    themes.append(
                        (
                            theme_name,
                            os.path.join(self.themes_path, theme, THEME_SPEC_FILE_NAME),
                        )
                    )
                else:
                    themes.append(theme_name)
        return themes

    def load(self, theme=None):
        if self.loaded_themes:
            for _theme in self.loaded_themes:
                if theme == _theme.name:
                    return _theme

        themes = self.list_themes(include_spec=True)
        theme_ = None
        for theme_name, theme_spec in themes:
            if theme:
                if theme_name != theme:
                    continue
            theme_ = Theme(os.path.dirname(theme_spec), theme_spec)
            self.loaded_themes.append(theme_)
            if theme:
                break
        if theme:
            return theme_
        return self.loaded_themes

    def cards(self):
        if not self.loaded_themes:
            return []
        cards = list()
        for theme in self.loaded_themes:
            cards.extend(theme.cards)
        return cards


if __name__ == "__main__":
    tm = ThemeManager()
    tm.load()
    print(tm.cards())
