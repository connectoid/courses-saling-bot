from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)


def get_main_menu():
    button_1: KeyboardButton = KeyboardButton(text='💳 Купить курсы')
    button_2: KeyboardButton = KeyboardButton(text='📚 Мои курсы')
    button_3: KeyboardButton = KeyboardButton(text='💅 О нас')
    button_4: KeyboardButton = KeyboardButton(text='❔ Помощь')

    main_menu_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                        keyboard=[[button_1, button_2],
                                                [button_3, button_4]],
                                        resize_keyboard=True)
    return main_menu_keyboard