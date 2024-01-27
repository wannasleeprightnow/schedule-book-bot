from handlers.divide_books_manually import router as \
    divide_books_manually_router
from handlers.divided_books import router as divided_books_router
from handlers.help import router as help_router
from handlers.profile import router as profile_router
from handlers.schedule import router as schedule_router
from handlers.start import router as start_router
from loader import dp


def include_routers():
    routers = [divide_books_manually_router, divided_books_router,
               help_router, profile_router, schedule_router, start_router]
    for router in routers:
        dp.include_router(router)
