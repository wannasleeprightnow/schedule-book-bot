from random import choice


def divide_books_list(books_ids: list[str]) -> list[list[str]]:
    books = list(set(books_ids))
    if len(books) % 2:
        last_elem = books.pop(-1)
        divided_books = [books[len(books) // 2 :], books[: len(books) // 2]]
        divided_books[choice([0, 1])].append(last_elem)
        return divided_books
    return [books[len(books) // 2 :], books[: len(books) // 2]]
