from __future__ import annotations

from typing import Any, Optional

from aiogram.types import InlineKeyboardButton

DEFAULT_BUTTON_COLOR = "default"


def _resolve_locale_entry(i18n: Any, lang: str, text_key: str, **kwargs: Any) -> Any:
    locales_data = getattr(i18n, "locales_data", {}) or {}
    lang_data = locales_data.get(lang) or locales_data.get(getattr(i18n, "default_lang", "en")) or locales_data.get("en") or {}
    return lang_data.get(text_key)


def build_inline_button(
    i18n: Any,
    lang: str,
    text_key: str,
    callback_data: Optional[str] = None,
    url: Optional[str] = None,
    fallback_text_key: Optional[str] = None,
    **kwargs: Any,
) -> InlineKeyboardButton:
    locale_entry = _resolve_locale_entry(i18n, lang, text_key, **kwargs)

    text: str
    metadata: dict[str, Any] = {"color": DEFAULT_BUTTON_COLOR}

    if isinstance(locale_entry, dict):
        text_template = locale_entry.get("text") or i18n.gettext(lang, text_key, **kwargs)
        metadata.update({
            "color": locale_entry.get("color", DEFAULT_BUTTON_COLOR),
            "custom_emoji_id": locale_entry.get("custom_emoji_id"),
        })
    else:
        text_template = i18n.gettext(lang, text_key, **kwargs)

    if text_template == text_key and fallback_text_key:
        text = i18n.gettext(lang, fallback_text_key, **kwargs)
    else:
        text = text_template

    button_kwargs: dict[str, Any] = {"text": text}
    if callback_data is not None:
        button_kwargs["callback_data"] = callback_data
    if url is not None:
        button_kwargs["url"] = url

    # Forward unsupported/new Telegram fields through api_kwargs where possible.
    api_kwargs: dict[str, Any] = {}
    if metadata.get("color") and metadata["color"] != DEFAULT_BUTTON_COLOR:
        api_kwargs["color"] = metadata["color"]
    if metadata.get("custom_emoji_id"):
        api_kwargs["custom_emoji_id"] = metadata["custom_emoji_id"]

    if api_kwargs:
        button_kwargs["api_kwargs"] = api_kwargs

    try:
        return InlineKeyboardButton(**button_kwargs)
    except TypeError:
        # Safe degradation for aiogram versions where api_kwargs/extra fields are not accepted.
        button_kwargs.pop("api_kwargs", None)
        return InlineKeyboardButton(**button_kwargs)
