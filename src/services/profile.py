import datetime

from config import FormatsConfig
from loader import database


async def get_user_profile(telegram_user_id: int) -> str:
    user = await database.get_user_grade_and_deskmate(telegram_user_id)
    grade = str(user.grade.number) + user.grade.letter
    deskmate = "@" + user.deskmate.telegram_username if user.deskmate else "-"
    notice_time = user.notice_time if user.notice_time else "-"
    return f"Класс: {grade}\nСосед по парте: \
{deskmate}\nВремя напоминаний: {notice_time}"


async def set_new_grade(telegram_user_id: int, grade: str) -> str:
    try:
        grade_id = await database.get_grade_id(grade)
    except ValueError:
        return "Вы ввели класс в неверном формате! Попробуйте снова."
    else:
        if grade_id is None:
            return "Вы ввели класс в неверном формате! Попробуйте снова."

    await database.update_user_grade(telegram_user_id, grade_id)

    return "Ваш класс успешно обновлен."


async def set_new_deskmate(
    telegram_user_id: int, deskmate_telegram_username: str
) -> str:

    if deskmate_telegram_username == "-":
        await delete_deskmate(telegram_user_id)
        return "Теперь у вас нет соседа по парте."

    deskmate = await database.get_deskmate(deskmate_telegram_username)
    current_deskmate = await database.get_user_deskmate(telegram_user_id)

    if deskmate is None:
        return "Такого пользователя не существует."

    elif deskmate.deskmate_id is not None:
        current_deskmate = await database.get_user_deskmate(telegram_user_id)
        if current_deskmate is not None:
            await database.delete_user_deskmate(current_deskmate.telegram_id)
        await database.delete_user_deskmate(telegram_user_id)
        await database.update_deskmate_username(
            telegram_user_id, deskmate_telegram_username
        )
        return "У этого пользователя уже \
есть сосед по парте. Изменить соседа по парте можно в профиле."

    else:
        current_deskmate = await database.get_user_deskmate(telegram_user_id)
        user = await database.get_user(telegram_user_id)
        if current_deskmate is not None:
            await database.delete_deskmate(current_deskmate.telegram_id)
        await database.update_deskmate_username(
            telegram_user_id, deskmate_telegram_username
        )
        await database.update_deskmate_username(
            deskmate.telegram_id, user.telegram_username
        )
        await database.update_user_deskmate(telegram_user_id, deskmate.id)
        await database.update_user_deskmate(deskmate.telegram_id, user.id)
        return "Вы успешно изменили соседа по парте."


async def delete_deskmate(telegram_user_id: int) -> None:
    current_deskmate = await database.get_user_deskmate(telegram_user_id)
    await database.delete_user_deskmate(current_deskmate.telegram_id)
    await database.delete_user_deskmate(telegram_user_id)


async def set_new_notice_time(telegram_user_id: int, notice_time: str) -> str:
    try:
        notice_time = datetime.time(
            *list(map(int, notice_time.split(":")))
        ).strftime(FormatsConfig.TIME_FORMAT)
        await database.update_user_notice_time(telegram_user_id, notice_time)
    except Exception:
        return "Проверьте корректность ввода."
    else:
        return "Ваше время напомианий изменено."


async def is_deskmate_exists(telegram_user_id: int) -> bool:
    deskmate = await database.get_user_deskmate(telegram_user_id)
    return False if deskmate is None else True
