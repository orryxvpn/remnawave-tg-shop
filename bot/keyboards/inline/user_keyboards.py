from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from typing import Dict, Optional, List, Tuple

from config.settings import Settings
from bot.services.button_catalog import get_button_text


def get_main_menu_inline_keyboard(
        lang: str,
        i18n_instance,
        settings: Settings,
        show_trial_button: bool = False) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()

    if show_trial_button and settings.TRIAL_ENABLED:
        builder.row(
            InlineKeyboardButton(text=_button("menu_activate_trial"),
                                 callback_data="main_action:request_trial"))

    builder.row(
        InlineKeyboardButton(text=_button("menu_subscribe"),
                             callback_data="main_action:subscribe"))
    builder.row(
        InlineKeyboardButton(
            text=_button("menu_my_subscription"),
            callback_data="main_action:my_subscription",
        )
    )

    promo_button = InlineKeyboardButton(
        text=_button("menu_apply_promo"),
        callback_data="main_action:apply_promo")
    if settings.REFERRAL_ENABLED:
        referral_button = InlineKeyboardButton(
            text=_button("menu_referral"),
            callback_data="main_action:referral")
        builder.row(referral_button, promo_button)
    else:
        builder.row(promo_button)

    language_button = InlineKeyboardButton(
        text=_button("menu_language_settings"),
        callback_data="main_action:language")
    status_button_list = []
    if settings.SERVER_STATUS_URL:
        status_button_list.append(
            InlineKeyboardButton(text=_button("menu_server_status"),
                                 url=settings.SERVER_STATUS_URL))

    if status_button_list:
        builder.row(language_button, *status_button_list)
    else:
        builder.row(language_button)

    if settings.SUPPORT_LINK:
        builder.row(
            InlineKeyboardButton(text=_button("menu_support"),
                                 url=settings.SUPPORT_LINK))

    if settings.TERMS_OF_SERVICE_URL:
        builder.row(
            InlineKeyboardButton(text=_button("menu_terms"),
                                 url=settings.TERMS_OF_SERVICE_URL))

    return builder.as_markup()


def get_language_selection_keyboard(i18n_instance,
                                    current_lang: str) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, current_lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.button(text=f"🇬🇧 English {'✅' if current_lang == 'en' else ''}",
                   callback_data="set_lang_en")
    builder.button(text=f"🇷🇺 Русский {'✅' if current_lang == 'ru' else ''}",
                   callback_data="set_lang_ru")
    builder.button(text=_button("back_to_main_menu"),
                   callback_data="main_action:back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_trial_confirmation_keyboard(lang: str,
                                    i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.button(text=_button("trial_confirm_activate"),
                   callback_data="trial_action:confirm_activate")
    builder.button(text=_button("cancel"),
                   callback_data="main_action:back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_subscription_options_keyboard(subscription_options: Dict[
    float, Optional[float]], currency_symbol_val: str, lang: str,
                                      i18n_instance, traffic_mode: bool = False) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    def _format_gb(val: float) -> str:
        return str(int(val)) if float(val).is_integer() else f"{val:g}"
    if subscription_options:
        for months, price in subscription_options.items():
            if price is not None:
                if traffic_mode:
                    button_text = _button(
                        "buy_traffic_package",
                        traffic_gb=_format_gb(months),
                        price=price,
                        currency_symbol=currency_symbol_val,
                    )
                    callback_data = f"subscribe_period:{_format_gb(months)}"
                else:
                    button_text = _button("subscribe_for_months",
                                    months=months,
                                    price=price,
                                    currency_symbol=currency_symbol_val)
                    callback_data = f"subscribe_period:{months}"
                builder.button(text=button_text,
                               callback_data=callback_data)
        builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text=_button("back_to_main_menu"),
                             callback_data="main_action:back_to_main"))
    return builder.as_markup()


def get_payment_method_keyboard(months: int, price: float,
                                stars_price: Optional[int],
                                currency_symbol_val: str, lang: str,
                                i18n_instance, settings: Settings, sale_mode: str = "subscription") -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    def _format_value(val: float) -> str:
        return str(int(val)) if float(val).is_integer() else f"{val:g}"
    value_str = _format_value(months)
    mode_suffix = f":{sale_mode}"
    for method in settings.payment_methods_order:
        if method == "severpay" and getattr(settings, "SEVERPAY_ENABLED", False):
            builder.button(
                text=_button("pay_with_severpay"),
                callback_data=f"pay_severpay:{value_str}:{price}{mode_suffix}",
            )
        elif method == "freekassa" and settings.FREEKASSA_ENABLED:
            builder.button(
                text=_button("pay_with_sbp"),
                callback_data=f"pay_fk:{value_str}:{price}{mode_suffix}",
            )
        elif method == "platega" and settings.PLATEGA_ENABLED:
            builder.button(
                text=_button("pay_with_platega"),
                callback_data=f"pay_platega:{value_str}:{price}{mode_suffix}",
            )
        elif method == "yookassa" and settings.YOOKASSA_ENABLED:
            builder.button(
                text=_button("pay_with_yookassa"),
                callback_data=f"pay_yk:{value_str}:{price}{mode_suffix}",
            )
        elif method == "stars" and settings.STARS_ENABLED and stars_price is not None:
            builder.button(
                text=_button("pay_with_stars"),
                callback_data=f"pay_stars:{value_str}:{stars_price}{mode_suffix}",
            )
        elif method == "cryptopay" and settings.CRYPTOPAY_ENABLED:
            builder.button(
                text=_button("pay_with_cryptopay"),
                callback_data=f"pay_crypto:{value_str}:{price}{mode_suffix}",
            )
    builder.button(text=_button("cancel"),
                   callback_data="main_action:subscribe")
    builder.adjust(1)
    return builder.as_markup()


def get_payment_url_keyboard(payment_url: str,
                             lang: str,
                             i18n_instance,
                             back_callback: Optional[str] = None,
                             back_text_key: str = "back_to_main_menu_button"
                             ) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.button(text=_button("pay"), url=payment_url)
    if back_callback:
        builder.button(text=get_button_text(back_text_key, i18n_instance, lang), callback_data=back_callback)
    else:
        builder.button(text=_button("back_to_main_menu"),
                       callback_data="main_action:back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_yk_autopay_choice_keyboard(
    months: int,
    price: float,
    lang: str,
    i18n_instance,
    has_saved_cards: bool = True,
    sale_mode: str = "subscription",
) -> InlineKeyboardMarkup:
    """Keyboard for choosing between saved card charge or new card payment when auto-renew is enabled."""
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    price_str = str(price)
    def _format_value(val: float) -> str:
        return str(int(val)) if float(val).is_integer() else f"{val:g}"
    value_str = _format_value(months)
    suffix = f":{sale_mode}"
    if has_saved_cards:
        builder.row(
            InlineKeyboardButton(
                text=_button("yookassa_autopay_pay_saved_card"),
                callback_data=f"pay_yk_saved_list:{value_str}:{price_str}{suffix}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=_button("yookassa_autopay_pay_new_card"),
            callback_data=f"pay_yk_new:{value_str}:{price_str}{suffix}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_button("back_to_payment_methods"),
            callback_data=f"subscribe_period:{value_str}",
        )
    )
    return builder.as_markup()


def get_yk_saved_cards_keyboard(
    cards: List[Tuple[str, str]],
    months: int,
    price: float,
    lang: str,
    i18n_instance,
    page: int = 0,
    sale_mode: str = "subscription",
) -> InlineKeyboardMarkup:
    """Paginated keyboard for selecting a saved YooKassa card."""
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    per_page = 5
    total = len(cards)
    start = page * per_page
    end = min(total, start + per_page)
    price_str = str(price)
    def _format_value(val: float) -> str:
        return str(int(val)) if float(val).is_integer() else f"{val:g}"
    value_str = _format_value(months)
    suffix = f":{sale_mode}"

    for method_id, title in cards[start:end]:
        builder.row(
            InlineKeyboardButton(
                text=title,
                callback_data=f"pay_yk_use_saved:{value_str}:{price_str}:{method_id}{suffix}",
            )
        )

    nav_buttons: List[InlineKeyboardButton] = []
    if start > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"pay_yk_saved_list:{value_str}:{price_str}:{page-1}{suffix}",
            )
        )
    if end < total:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"pay_yk_saved_list:{value_str}:{price_str}:{page+1}{suffix}",
            )
        )
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text=_button("yookassa_autopay_pay_new_card"),
            callback_data=f"pay_yk_new:{value_str}:{price_str}{suffix}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_button("back_to_autopay_method_choice"),
            callback_data=f"pay_yk:{value_str}:{price_str}{suffix}",
        )
    )
    return builder.as_markup()


def get_referral_link_keyboard(lang: str,
                               i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.button(text=_button("referral_share_message"),
                   callback_data="referral_action:share_message")
    builder.button(text=_button("back_to_main_menu"),
                   callback_data="main_action:back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_back_to_main_menu_markup(lang: str,
                                 i18n_instance,
                                 callback_data: Optional[str] = None) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    if callback_data:
        builder.button(text=_button("back_to_main_menu"),
                       callback_data=callback_data)
    else:
        builder.button(text=_button("back_to_main_menu"),
                       callback_data="main_action:back_to_main")
    return builder.as_markup()


def get_subscribe_only_markup(lang: str, i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.button(text=_button("menu_subscribe"),
                   callback_data="main_action:subscribe")
    return builder.as_markup()


def get_user_banned_keyboard(support_link: Optional[str], lang: str,
                             i18n_instance) -> Optional[InlineKeyboardMarkup]:
    if not support_link:
        return None
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.button(text=_button("menu_support"), url=support_link)
    return builder.as_markup()


def get_channel_subscription_keyboard(
        lang: str,
        i18n_instance,
        channel_link: Optional[str],
        include_check_button: bool = True) -> Optional[InlineKeyboardMarkup]:
    """
    Return keyboard with buttons to open the required channel and trigger a subscription re-check.
    """
    if i18n_instance is None:
        return None

    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()

    has_buttons = False

    if channel_link:
        builder.button(
            text=_button("channel_subscription_join"),
            url=channel_link,
        )
        has_buttons = True

    if include_check_button:
        builder.button(
            text=_button("channel_subscription_verify"),
            callback_data="channel_subscription:verify",
        )
        has_buttons = True

    if not has_buttons:
        return None

    builder.adjust(1)
    return builder.as_markup()


def get_connect_and_main_keyboard(
        lang: str,
        i18n_instance,
        settings: Settings,
        config_link: Optional[str],
        connect_button_url: Optional[str] = None,
        preserve_message: bool = False) -> InlineKeyboardMarkup:
    """Keyboard with a connect button and a back to main menu button."""
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    button_target = connect_button_url or config_link

    if settings.SUBSCRIPTION_MINI_APP_URL:
        builder.row(
            InlineKeyboardButton(
                text=_button("connect"),
                web_app=WebAppInfo(url=settings.SUBSCRIPTION_MINI_APP_URL),
            )
        )
    elif button_target:
        builder.row(
            InlineKeyboardButton(text=_button("connect"), url=button_target)
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=_button("connect"),
                callback_data="main_action:my_subscription",
            )
        )

    back_callback = "main_action:back_to_main_keep" if preserve_message else "main_action:back_to_main"
    builder.row(
        InlineKeyboardButton(
            text=_button("back_to_main_menu"),
            callback_data=back_callback,
        )
    )

    return builder.as_markup()


def get_payment_methods_manage_keyboard(lang: str, i18n_instance, has_card: bool) -> InlineKeyboardMarkup:
    """Deprecated in favor of get_payment_methods_list_keyboard. Kept for backward compatibility."""
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_button("payment_method_bind"), callback_data="pm:bind")
    )
    builder.row(
        InlineKeyboardButton(text=_button("back_to_main_menu"), callback_data="main_action:back_to_main")
    )
    return builder.as_markup()


def get_payment_methods_list_keyboard(
    cards: List[Tuple[str, str]],
    page: int,
    lang: str,
    i18n_instance,
) -> InlineKeyboardMarkup:
    """
    Build a paginated list of saved payment methods.
    cards: list of tuples (payment_method_id, display_title)
    page: 0-based page index
    """
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    per_page = 5
    total = len(cards)
    start = page * per_page
    end = start + per_page
    for pm_id, title in cards[start:end]:
        builder.row(
            InlineKeyboardButton(text=title, callback_data=f"pm:view:{pm_id}")
        )

    # Pagination controls if needed
    nav_buttons: List[InlineKeyboardButton] = []
    if start > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"pm:list:{page-1}"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"pm:list:{page+1}"))
    if nav_buttons:
        builder.row(*nav_buttons)

    # Bind new card and back
    builder.row(InlineKeyboardButton(text=_button("payment_method_bind"), callback_data="pm:bind"))
    builder.row(InlineKeyboardButton(text=_button("back_to_main_menu"), callback_data="main_action:back_to_main"))
    return builder.as_markup()


def get_payment_method_delete_confirm_keyboard(pm_id: str, lang: str, i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_button("yes"), callback_data=f"pm:delete:{pm_id}"),
        InlineKeyboardButton(text=_button("cancel"), callback_data=f"pm:view:{pm_id}"),
    )
    return builder.as_markup()


def get_payment_method_details_keyboard(pm_id: str, lang: str, i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_button("payment_method_tx_history"), callback_data=f"pm:history:{pm_id}")
    )
    builder.row(
        InlineKeyboardButton(text=_button("payment_method_delete"), callback_data=f"pm:delete_confirm:{pm_id}")
    )
    builder.row(
        InlineKeyboardButton(text=_button("back_to_main_menu"), callback_data="pm:list:0")
    )
    return builder.as_markup()


def get_bind_url_keyboard(bind_url: str, lang: str, i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.button(text=_button("payment_method_bind"), url=bind_url)
    builder.button(text=_button("back_to_main_menu"), callback_data="pm:manage")
    builder.adjust(1)
    return builder.as_markup()


def get_back_to_payment_methods_keyboard(lang: str, i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=_button("back_to_main_menu"), callback_data="pm:list:0"))
    return builder.as_markup()


def get_back_to_payment_method_details_keyboard(pm_id: str, lang: str, i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    # Back one step: return to specific payment method details
    builder.row(InlineKeyboardButton(text=_button("back_to_main_menu"), callback_data=f"pm:view:{pm_id}"))
    return builder.as_markup()


def get_autorenew_cancel_keyboard(lang: str, i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_button("autorenew_disable"), callback_data="autorenew:cancel")
    )
    builder.row(
        InlineKeyboardButton(text=_button("menu_my_subscription"), callback_data="main_action:my_subscription")
    )
    return builder.as_markup()


def get_autorenew_confirm_keyboard(enable: bool, sub_id: int, lang: str, i18n_instance) -> InlineKeyboardMarkup:
    _button = lambda button_id, **kwargs: get_button_text(button_id, i18n_instance, lang, **kwargs)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_button("yes"), callback_data=f"autorenew:confirm:{sub_id}:{1 if enable else 0}"),
        InlineKeyboardButton(text=_button("no"), callback_data="main_action:my_subscription"),
    )
    return builder.as_markup()
