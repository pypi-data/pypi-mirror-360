from pathlib import Path


def to_camel_case(snake_str: str) -> str:
    """Преобразует snake_case в CamelCase"""
    return ''.join(word.title() for word in snake_str.split('_'))


def create_handler_template(function_name: str, target_dir: Path):
    """Создает файл обработчика"""
    camel_case = to_camel_case(function_name)

    content = f"""from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

import api.database.requests as rq
import bot.{function_name}.{function_name}_keyboard as kb
from bot.{function_name}.{function_name}_states import States
import global_states
import global_keyboards


router = Router()

# Ваши обработчики здесь
# @router.message(Command('start'))
# async def cmd_start(message: Message):
#     ...
"""
    (target_dir / f"{function_name}_handler.py").write_text(content)


def create_keyboard_template(function_name: str, target_dir: Path):
    """Создает файл клавиатуры"""
    content = """from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

# Пример создания клавиатуры:
# def main_kb():
#     builder = InlineKeyboardBuilder()
#     builder.button(text="Кнопка", callback_data="callback_data")
#     return builder.as_markup()
"""
    (target_dir / f"{function_name}_keyboard.py").write_text(content)


def create_states_template(function_name: str, target_dir: Path):
    """Создает файл состояний"""
    camel_case = to_camel_case(function_name)

    content = f"""from aiogram.fsm.state import StatesGroup, State

class States(StatesGroup):
    # Добавьте нужные состояния
    main_state = State()
    # example_state = State()
"""
    (target_dir / f"{function_name}_states.py").write_text(content)