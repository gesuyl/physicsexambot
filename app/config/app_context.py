from aiogram import Bot, Dispatcher

from app.database import Database
from app.image_reader import ImageReader

from .config import settings


class AppContext:
    """
    Class that contains main app objects
    """
    def __init__(self) -> None:
        """
        Constructor that initializes AppContext object
        """
        self.tesseract_reader = ImageReader(Database("sqlite:///physexambot.db"))
        self.bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), parse_mode='HTML')
        self.dispatcher = Dispatcher()

        print("[#] AppContext created")


app_context = AppContext()