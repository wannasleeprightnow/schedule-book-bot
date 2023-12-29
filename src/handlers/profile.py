from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.profile import builder as profile_keyboard

profile_router = Router()


class UserGrade(StatesGroup):
    grade = State()


class UserDeskmate(StatesGroup):
    deskmate = State()


class UserNotice(StatesGroup):
    notice_time = State()


@profile_router.message(F.text == "Профиль")
async def command_profile_handler(message: Message):
    await message.answer(
        "Ваш профиль",
        reply_markup=profile_keyboard.as_markup(resize_keyboard=True))


@profile_router.callback_query(F.data == "Изменить класс")
async def change_grade(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите класс, в котором Вы учитесь")
    await state.set_state(UserGrade.grade)


@profile_router.message(UserGrade.grade)
async def grade_choosen(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    await message.answer("Ваш класс обновлен")
    await state.clear()


@profile_router.callback_query(F.data == "Изменить соседа по парте")
async def change_deskmate(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите имя пользователя Вашего соседа по парте")
    await state.set_state(UserDeskmate.deskmate)


@profile_router.message(UserDeskmate.deskmate)
async def deskmate_choosen(message: Message, state: FSMContext):
    await state.update_data(deskmate=message.text)
    await message.answer("Ваш сосед по парте обновлен")
    await state.clear()


@profile_router.callback_query(F.data == "Изменить время напоминаний")
async def change_notice_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите время напоминаний")
    await state.set_state(UserDeskmate.deskmate)


@profile_router.message(UserNotice.notice_time)
async def notice_time_choosen(message: Message, state: FSMContext):
    await state.update_data(notice_time=message.text)
    await message.answer("Ваше время напоминаний обновлено")
    await state.clear()
