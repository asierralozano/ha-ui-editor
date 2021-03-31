import os

import typing

from homeassistant_ui_editor.settings import HomeAssistantUIEditorSettings
from homeassistant_ui_editor.constants import SETTINGS_THEMES_PATH, THEME_SPEC_FILE_NAME, CARDS_EXTENSION

SETTINGS = HomeAssistantUIEditorSettings()


class Theme(object):

    def __init__(self, theme_path):
        self._theme_path = theme_path

    @property
    def theme_path(self) -> str:
        return self._theme_path

    @property
    def name(self):
        return os.path.basename(self.theme_path)

    @property
    def card_types(self):
        card_types = list()
        for _file in os.listdir(self.theme_path):
            if os.path.isfile(os.path.join(self.theme_path, _file)):
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


class ThemeManager(object):
    def __init__(self, themes_path=SETTINGS.get(SETTINGS_THEMES_PATH)):
        self._themes_path = themes_path
        self._loaded_themes = list()

    @property
    def themes_path(self) -> str:
        return self._themes_path

    @property
    def loaded_themes(self) -> typing.List[typing.Optional[Theme]]:
        return self._loaded_themes

    def list_themes(self, include_path=False):
        themes = list()
        for theme in os.listdir(self.themes_path):
            if os.path.isfile(
                os.path.join(self.themes_path, theme, THEME_SPEC_FILE_NAME)
            ):
                if include_path:
                    themes.append((theme, os.path.join(self.themes_path, theme)))
                else:
                    themes.append(theme)
        return themes

    def load(self, theme=None):
        themes = self.list_themes(include_path=True)
        for theme_name, theme_path in themes:
            if theme:
                if theme_name != theme:
                    continue
            self.loaded_themes.append(Theme(theme_path))
            if theme:
                break
        return self.loaded_themes

    def cards(self):
        if not self.loaded_themes:
            return []
        cards = list()
        for theme in self.loaded_themes:
            cards.extend(theme.cards)
        return cards


if __name__ == '__main__':
    tm = ThemeManager()
    tm.load()
    print(tm.cards())