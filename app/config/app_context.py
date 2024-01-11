from aiogram import Bot, Dispatcher
#
from app.database import Database
from app.image_reader import ImageReader
from .config import settings

class AppContext:
    def __init__(self):
        self.db = Database("sqlite:///physexambot.db")
        self.tesseract_reader = ImageReader(self.db)
        self.tesseract_reader.update_info()
        self.bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), parse_mode='HTML')
        self.dispatcher = Dispatcher()

app_context = AppContext()