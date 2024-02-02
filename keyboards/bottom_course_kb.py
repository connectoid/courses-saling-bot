from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_bottom_keyboard(*buttons: str) -> InlineKeyboardMarkup:
    print(*buttons)
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*[InlineKeyboardButton(
        text=button.split('_')[0],
        callback_data=button) for button in buttons],
        width=2)
    return kb_builder.as_markup()


def create_url_keyboard(text, url):
    url_button_1 = InlineKeyboardButton(
        text=text,
        url=url
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[url_button_1]]
    )
    return keyboard