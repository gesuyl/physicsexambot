from re import S
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import os
from platform import system



class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    STORED_IMAGES_FOLDER: str
    PROC_IMAGES_FOLDER: str
    TESSERACT_BIN: str = None


    # @classmethod
    # def set_tesseract_bin(cls, settings):
    platform_to_tesseract = {
        "Windows": r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        "Linux": '/usr/bin/tesseract',
        "Darwin": '/usr/local/bin/tesseract',
    }
    TESSERACT_BIN = platform_to_tesseract.get(system(), 'tesseract')

    print(f'Tesseract binary path set to: {TESSERACT_BIN}')


    def ensure_folders_exist(settings):
        for folder_path in [settings.STORED_IMAGES_FOLDER, settings.PROC_IMAGES_FOLDER]:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f'Created folder: {folder_path}')

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
    
        
settings = Settings()
Settings.ensure_folders_exist(settings)

try:
    print(settings.TESSERACT_BIN)
    
except KeyError as e:
    if e.args[0] == 'TESSERACT_BIN':
        print('Tesseract binary path not set.')
        Settings.set_tesseract_bin(settings)

print(settings.model_dump_json())
exit()

config = Settings()
