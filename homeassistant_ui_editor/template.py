import os

import jinja2

from .constants import SETTINGS_THEMES_PATH
from .settings import HomeAssistantUIEditorSettings
from .theme_manager import ThemeManager


SETTINGS = HomeAssistantUIEditorSettings()


def _render_jinja(template: str, theme: str, template_type: str, **context) -> str:
    theme_manager = ThemeManager()
    theme = theme_manager.load(theme)
    templates_path = os.path.join(
        theme.theme_path, template_type, "templates"
    )
    template_loader = jinja2.FileSystemLoader(searchpath=templates_path)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template)
    return template.render(**context)


if __name__ == "__main__":
    # print(_render_jinja("room_button.j2", title="aaa", path="bbb", cards=["aaaa", "bbb", "vvv"]))
    print(_render_jinja("room_button.j2", name="aaa", path="bbb", entity="light.laa"))
