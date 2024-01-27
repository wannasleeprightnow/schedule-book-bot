from random import choice


def divide_books(user_id, deskmate_id, books_id):
    books = list(set(books_id))
    if len(books) % 2:
        elem = books.pop(-1)
    devided = {
        "first_deskmate_books": ", ".join(books[: len(books) // 2]),
        "second_deskmate_books": ", ".join(books[len(books) // 2 :]),
        "first_deskmate_id": user_id,
        "second_deskmate_id": deskmate_id,
        "schedule_id": ...,
    }
    if len(books) % 2:
        devided[choice(["first_deskmate_books", "second_deskmate_books"])] += (
            ", " + elem
        )
    return devided
