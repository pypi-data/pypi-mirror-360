from .api import flash_stock, flash_recovery, flash_boot
from questionary import Style


pointer = '-->'

custom_style = Style([
    ('questionmark', 'fg:#673ab7 bold'),  # Фиолетовый жирный знак вопроса
    ('question', 'bold fg:ansicyan'),  # <<< ГОЛУБОЙ ЖИРНЫЙ ТЕКСТ ВОПРОСА
    ('selected', 'fg:#d2da44 bg:'),  # цвет для выбранного элемента
    ('pointer', 'fg:#e0eb16 bold'),  # указатель
    ('answer', 'fg:#e0eb16 bold'),  # жирный ответ после выбора
])