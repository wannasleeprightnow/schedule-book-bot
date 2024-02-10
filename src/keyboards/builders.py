import datetime

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import FormatsConfig


def dates_keyboard_builder(
    dates: list[datetime.date], callback_prefix: str
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for date in dates:
        formated_date = date.strftime(FormatsConfig.DATE_FORMAT)
        builder.add(
            InlineKeyboardButton(
                text=formated_date,
                callback_data=callback_prefix + str(date),
            )
        )
    return builder


def books_list_builder(books_list: list[str]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for book in set(books_list):
        builder.add(
            InlineKeyboardButton(
                text=book,
                callback_data="wanna_give_" + book,
            )
        )
    builder.add(InlineKeyboardButton(text="Готово", callback_data="stop"))
    return builder
