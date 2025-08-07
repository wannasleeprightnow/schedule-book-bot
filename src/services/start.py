from loader import database


async def register_user(
    telegram_id: int,
    grade: str,
    deskmate_telegram_username: str,
    telegram_username: str,
) -> str:
    deskmate = await database.get_deskmate(deskmate_telegram_username)

    try:
        grade_id = await database.get_grade_id(grade)
    except ValueError:
        return "Вы ввели класс в неверном формате! Попробуйте снова."
    else:
        if grade_id is None:
            return "Вы ввели класс в неверном формате! Попробуйте снова."

    if deskmate and deskmate.deskmate_id is None:
        user_id = await database.insert_user(
            telegram_id,
            telegram_username,
            deskmate_telegram_username,
            grade_id,
            deskmate.id,
        )
        await database.update_deskmate(user_id, deskmate.id)
        return "Вы успешно зарегистрировались!"

    await database.insert_user(
        telegram_id, telegram_username, deskmate_telegram_username, grade_id
    )

    if deskmate is None:
        return "Вы успешно зарегистрировались, но ваш сосед по парте пока нет."

    elif deskmate.deskmate_id:
        return (
            "Вы успешно зарегистрировались, но у этого пользователя"  # noqa: RUF001
            "уже есть сосед по парте. Изменить соседа по парте "
            "можно в профиле."
        )
