from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
import os
from platform import system


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    STORED_IMAGES_FOLDER: str
    PROC_IMAGES_FOLDER: str
    TESSERACT_BIN: str


    @classmethod
    def set_tesseract_bin(cls):
        platform_to_tesseract = {
            "Windows": r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            "Linux": '/usr/bin/tesseract',
            "Darwin": '/usr/local/bin/tesseract',
        }
        os_ = system()
        print('Detected OS:', os_)
              
        cls.TESSERACT_BIN = platform_to_tesseract.get(os_, 'tesseract')

        print(f'Tesseract binary path set to: {cls.TESSERACT_BIN}')


    def ensure_folders_exist(self):
        for folder_path in [self.STORED_IMAGES_FOLDER, self.PROC_IMAGES_FOLDER]:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f'Created folder: {folder_path}')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    
        
print('Reading config...')

settings = Settings()

if not settings.TESSERACT_BIN:
    print('Tesseract binary path not set')
    Settings.set_tesseract_bin()
    settings.TESSERACT_BIN = Settings.TESSERACT_BIN

settings.ensure_folders_exist()
