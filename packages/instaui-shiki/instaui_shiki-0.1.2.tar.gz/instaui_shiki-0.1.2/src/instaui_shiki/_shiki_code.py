from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional
from instaui import ui
from instaui.runtime._app import get_app_slot

_STATIC_DIR = Path(__file__).parent / "static"
_THEME_DIR = _STATIC_DIR / "themes"
_LANG_DIR = _STATIC_DIR / "langs"
_SHIKI_TRANSFORMERS_FILE = _STATIC_DIR / "shiki-transformers.js"
_STYLE = _STATIC_DIR / "shiki-style.css"


_LANGS_IMPORT_NAME = "@shiki/langs/"
_THEMES_IMPORT_NAME = "@shiki/themes/"

_IMPORT_MAPS = {
    "@shiki/transformers": _SHIKI_TRANSFORMERS_FILE,
    _LANGS_IMPORT_NAME: _LANG_DIR,
    _THEMES_IMPORT_NAME: _THEME_DIR,
}

_ZERO_IMPORT_MAPS = {
    "@shiki/transformers": _SHIKI_TRANSFORMERS_FILE,
    f"{_LANGS_IMPORT_NAME}python.mjs": _LANG_DIR / "python.mjs",
    f"{_THEMES_IMPORT_NAME}vitesse-light.mjs": _THEME_DIR / "vitesse-light.mjs",
    f"{_THEMES_IMPORT_NAME}vitesse-dark.mjs": _THEME_DIR / "vitesse-dark.mjs",
}


class Code(
    ui.element,
    esm="./static/shiki_code.js",
    externals=_IMPORT_MAPS,
    css=[_STYLE],
):
    # _language_folder: ClassVar[Path] = _LANGUAGE_DIR

    def __init__(
        self,
        code: ui.TMaybeRef[str],
        *,
        language: Optional[ui.TMaybeRef[str]] = None,
        theme: Optional[ui.TMaybeRef[str]] = None,
        themes: Optional[Dict[str, str]] = None,
        transformers: Optional[List[TTransformerNames]] = None,
        line_numbers: Optional[ui.TMaybeRef[bool]] = None,
    ):
        super().__init__()
        self.props({"code": code})

        if language:
            self.props({"language": language})

        if theme:
            self.props({"theme": theme})

        if themes:
            self.props({"themes": themes})

        if transformers:
            self.props({"transformers": transformers})

        if line_numbers is not None:
            self.props({"lineNumbers": line_numbers})

    def _to_json_dict(self):
        self.use_zero_dependency()
        return super()._to_json_dict()

    def use_zero_dependency(self):
        app = get_app_slot()
        tag_name = self.dependency.tag_name  # type: ignore

        if app.mode != "zero" or app.has_temp_component_dependency(tag_name):
            return

        self.update_dependencies(
            css=[_STYLE], externals=_ZERO_IMPORT_MAPS, replace=True
        )

    @staticmethod
    def update_zero_dependency(add_languages: Optional[Iterable[str]] = None):
        if isinstance(add_languages, str):
            add_languages = [add_languages]

        for lang in add_languages or []:
            name = f"{_LANGS_IMPORT_NAME}{lang}.mjs"
            path = _LANG_DIR / f"{lang}.mjs"
            _ZERO_IMPORT_MAPS[name] = path


TTransformerNames = Literal["notationDiff"]
