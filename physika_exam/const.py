import os
from platform import system


STORED_IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'img_processing', 'stored_images')
IMG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'img_processing')

if not os.path.exists(STORED_IMAGES_FOLDER):
    os.makedirs(STORED_IMAGES_FOLDER)

if not os.path.exists(IMG_PATH):
    os.makedirs(IMG_PATH)

platform_to_tesseract = {
    "Windows": 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
    "Linux": 'tesseract',
    "Darwin": 'tesseract',
}

TESSERACT_CMD = platform_to_tesseract.get(system(), 'tesseract')
