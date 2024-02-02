from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, Text, StateFilter
from aiogram.types import (CallbackQuery, Message, ReplyKeyboardRemove, 
                           LabeledPrice, PreCheckoutQuery, ContentType)
from aiogram.types.message import ContentType
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from keyboards.commands_menu import set_commands_menu
from keyboards.bottom_course_kb import create_bottom_keyboard, create_url_keyboard
from keyboards.main_menu import get_main_menu
from config_data.config import Config, load_config
from database.orm import (add_user, get_user_id, get_all_courses, get_course, add_course,
                          get_user_courses)

router = Router()
config: Config = load_config()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

# @router.message(~F.text)
# async def content_type_example(msg: Message):
#     await msg.answer('👍')


@router.message(CommandStart())
async def process_start_command(message: Message):
    fname = message.from_user.first_name
    lname = message.from_user.last_name
    tg_id = message.from_user.id
    if add_user(tg_id, fname, lname):
        await message.answer(
        text=f'Здравствуйте {fname} {lname}! Вы запустили бот для покупки курсов.',
        reply_markup=get_main_menu())
    else:
        await message.answer(
        text=f'С возвращением {fname} {lname}! Вы запустили бот для покупки курсов.',
        reply_markup=get_main_menu())


@router.message(Command(commands='help'))
@router.message(Text(text='❔ Помощь'))
async def process_start_command(message: Message):
    await message.answer(
        text=f'Здесь будет текст справочной информации по работе с ботом.',
        reply_markup=get_main_menu())


@router.message(Text(text='💅 О нас'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text=f'Салон красоты «Полина» находится по адресу: Московская область, г. Ступино, ул. Бахарева, д. 10/39',
        reply_markup=get_main_menu())


@router.message(Text(text='💳 Купить курсы'))
async def process_buy_courses(message: Message):
    user_id = message.from_user.id
    all_courses = get_all_courses(user_id)
    courses = [course.name for course in all_courses]
    print(courses)
    if courses:
        for course in all_courses:
            await message.answer(
                text=f'<b>{course.name}</b>\n\n<i>{course.description}</i>\n\n Цена: {course.price} руб.',
                reply_markup=create_bottom_keyboard(
                f'Подробнее_{course.id}', f'Купить_{course.id}')
            )
    else:
        await message.answer(
                text=f'Вы уже купили все курсы. Новых курсов пока нет.',
                reply_markup=get_main_menu()
            )


@router.message(Text(text='📚 Мои курсы'))
async def process_buy_courses(message: Message):
    user_id = message.from_user.id
    user_courses = get_user_courses(user_id)
    print(user_courses)
    if user_courses:
        for course in user_courses:
            await message.answer(
                text=f'<b>{course.name}</b>\n\n<i>{course.description}</i>',
                reply_markup=create_url_keyboard('Перейти на курс', course.course_url),
                parse_mode=ParseMode.HTML
            )
    else:
        await message.answer(
                text=f'У вас пока нет купленных курсов.',
                reply_markup=get_main_menu()
            )


@router.callback_query(Text(startswith='Подробнее'))
async def process_detail_course(callback: CallbackQuery):
    # user_id = get_user_id(callback.from_user.id)
    course_id = callback.data.split('_')[1]
    course = get_course(course_id)
    await callback.message.edit_text(text=f'{course.description_full}\n\n Цена: {course.price} руб.',
                                  reply_markup=create_bottom_keyboard(
                                f'Назад_{course.id}', f'Купить_{course.id}'
                            ))


@router.callback_query(Text(startswith='Назад'))
async def process_detail_course(callback: CallbackQuery):
    # user_id = get_user_id(callback.from_user.id)
    course_id = callback.data.split('_')[1]
    course = get_course(course_id)
    await callback.message.edit_text(
            text=f'<b>{course.name}</b>\n\n<i>{course.description}</i>\n\n Цена: {course.price} руб.',
                            reply_markup=create_bottom_keyboard(
                                f'Подробнее_{course.id}', f'Купить_{course.id}'
                            )
            )
  

@router.callback_query(Text(startswith='Купить'))
async def process_buy_course(callback: CallbackQuery):
    course_id = callback.data.split('_')[1]
    course = get_course(course_id)
    PAYMENTS_PROVIDER_TOKEN = config.payment.paymen_provider_token
    TITLE = f'{course.name}'
    TIME_MACHINE_IMAGE_URL = 'http://'
    PRICE = LabeledPrice(label=TITLE, amount=course.price)
    DESCRIPTION = text=f'{course.description}'
    await bot.send_invoice(
            callback.message.chat.id,
            title=TITLE,
            description=DESCRIPTION,
            provider_token=PAYMENTS_PROVIDER_TOKEN,
            currency='rub',
            photo_url=TIME_MACHINE_IMAGE_URL,
            photo_height=512,  # !=0/None, иначе изображение не покажется
            photo_width=512,
            photo_size=512,
            is_flexible=False,  # True если конечная цена зависит от способа доставки
            prices=[PRICE],
            start_parameter='time-machine-example',
            payload=course_id
        )


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    print('PRE CHECKOUT QUERY')
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    print(pre_checkout_query)



# successful payment
@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment
    course_id = payment_info.invoice_payload
    course = get_course(course_id)
    add_course(message.from_user.id, course_id)
    msg=(f'Платеж на сумму {message.successful_payment.total_amount // 100} '
        f'{message.successful_payment.currency} прошел успешно!\n'
        f'Курс "{course.name}" добавлен в Ваши курсы.')
    await message.answer(msg, reply_markup=get_main_menu())
