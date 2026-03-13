import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ButtonModel:
    text_key: str
    emoji: Optional[str] = None
    style: str = "secondary"


class ButtonCatalog:
    ALLOWED_STYLES = {"primary", "secondary", "danger", "success"}

    def __init__(self, config_path: str = "locales/buttons.json") -> None:
        self.config_path = Path(config_path)
        self._buttons = self._load_and_validate()

    def _load_and_validate(self) -> Dict[str, ButtonModel]:
        raw = json.loads(self.config_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Button catalog must be a JSON object")

        buttons: Dict[str, ButtonModel] = {}
        for button_id, data in raw.items():
            if not isinstance(button_id, str) or not button_id:
                raise ValueError("Each button_id must be a non-empty string")
            if not isinstance(data, dict):
                raise ValueError(f"Button '{button_id}' must be an object")

            text_key = data.get("text_key")
            emoji = data.get("emoji")
            style = data.get("style", "secondary")

            if not isinstance(text_key, str) or not text_key:
                raise ValueError(f"Button '{button_id}': text_key must be a non-empty string")
            if emoji is not None and not isinstance(emoji, str):
                raise ValueError(f"Button '{button_id}': emoji must be a string or null")
            if not isinstance(style, str) or style not in self.ALLOWED_STYLES:
                raise ValueError(
                    f"Button '{button_id}': style must be one of {sorted(self.ALLOWED_STYLES)}"
                )

            buttons[button_id] = ButtonModel(text_key=text_key, emoji=emoji, style=style)

        return buttons

    def get(self, button_id: str) -> ButtonModel:
        button = self._buttons.get(button_id)
        if button is None:
            raise KeyError(f"Button with id '{button_id}' not found in catalog")
        return button

    def render_text(self, button_id: str, i18n_instance: Any, lang: str, **kwargs: Any) -> str:
        button = self.get(button_id)
        localized_text = i18n_instance.gettext(lang, button.text_key, **kwargs)
        if button.emoji:
            return f"{button.emoji} {localized_text}"
        return localized_text


_button_catalog_singleton: Optional[ButtonCatalog] = None


def get_button_catalog(config_path: str = "locales/buttons.json") -> ButtonCatalog:
    global _button_catalog_singleton
    if _button_catalog_singleton is None:
        _button_catalog_singleton = ButtonCatalog(config_path=config_path)
    return _button_catalog_singleton


def get_button_text(button_id: str, i18n_instance: Any, lang: str, **kwargs: Any) -> str:
    return get_button_catalog().render_text(button_id=button_id, i18n_instance=i18n_instance, lang=lang, **kwargs)
