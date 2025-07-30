from pathlib import Path


def to_camel_case(snake_str: str) -> str:
    """Преобразует snake_case в CamelCase"""
    return ''.join(word.title() for word in snake_str.split('_'))


def create_handler_template(function_name: str, target_dir: Path):
    """Создает файл обработчика"""
    camel_case = to_camel_case(function_name)

    content = f"""from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import api.database.requests as rq

import bot.{function_name}.{function_name}_keyboard as kb
from bot.{function_name}.{function_name}_states import States

import GlobalStates
import global_keyboards


router = Router()

# Ваши обработчики здесь
"""
    (target_dir / f"{function_name}_handler.py").write_text(content)


def create_keyboard_template(function_name: str, target_dir: Path):
    """Создает файл клавиатуры"""
    content = """from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

"""
    (target_dir / f"{function_name}_keyboard.py").write_text(content)


def create_states_template(function_name: str, target_dir: Path):
    """Создает файл состояний"""
    camel_case = to_camel_case(function_name)

    content = f"""from aiogram.fsm.state import StatesGroup, State

class States(StatesGroup):
    # Добавьте нужные состояния
    # example_state = State()
"""
    (target_dir / f"{function_name}_states.py").write_text(content)

def create_dot_env(target_dir: Path):
    content = f'TOKEN="token"'
    (target_dir / ".env").write_text(content)

def create_main(target_dir: Path):
    content = """import asyncio
import importlib
import os
from dotenv import load_dotenv

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import api.database.requests as rq
from api.database.models import async_main

import bot.commands.commands as commands
import bot.admin.admin as admin



load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")

global bot

async def import_routers(dp):
    dp.include_router(commands.router)
    dp.include_router(admin.router)
    handlers_dir = os.path.join(os.path.dirname(__file__), 'bot')
    main_handler = None
    for dir in os.listdir(handlers_dir):
        try: os.listdir(os.path.join(os.path.dirname(__file__), f'bot/{dir}'))
        except NotADirectoryError:
            continue
        for filename in os.listdir(os.path.join(os.path.dirname(__file__), f'bot/{dir}')):
            if filename.endswith('handler.py'):
                module_name = f'bot.{dir}.{filename[:-3]}'

                if filename == 'main.py':
                    main_handler = module_name
                else:
                    module = importlib.import_module(module_name)
                    if hasattr(module, 'router'):
                        dp.include_router(module.router)
    if main_handler:
        module = importlib.import_module(main_handler)
        if hasattr(module, 'router'):
            dp.include_router(module.router)



async def main():
    await async_main()

    global bot
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    await import_routers(dp)

    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
        """

    (target_dir / "main.py").write_text(content)


def create_admin_handler(target_dir: Path):
    content = """from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

import api.database.requests as rq

import bot.admin.admin_keyboard as kb
from bot.admin.admin_states import Admin

import GlobalStates
import global_keyboards

router = Router()

@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    if message.from_user.id in await rq.get_admins():
        await message.delete()
        await message.answer('Админ функции', reply_markup=kb.admin_buttons)
        await state.set_state(Admin.admin)"""


    (target_dir / "admin" / "admin.py").write_text(content)

def create_admin_keyboards(target_dir: Path):
    content = """from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

admin_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [

        ]
    ]
)"""

    (target_dir / "admin" / "admin_keyboard.py").write_text(content)

def create_admin_states(target_dir: Path):
    content = """from aiogram.fsm.state import StatesGroup, State

class Admin(StatesGroup):
    admin = State()
    pass"""

    (target_dir / "admin" / "admin_states.py").write_text(content)

def create_admin(target_dir: Path):
    create_admin_handler(target_dir)
    create_admin_keyboards(target_dir)
    create_admin_states(target_dir)

def create_commands_handler(target_dir: Path):
    content = """from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

import api.database.requests as rq

import bot.commands.admin_keyboard as kb
from bot.commands.commands_states import States

import GlobalStates
import global_keyboards

router = Router()


router = Router()



@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await message.delete()
    try:
        await data['main_message'].edit_text('Приветствие', reply_markup=global_keyboards.user_buttons))
    except:
        await state.update_data(main_message = await message.answer("Приветствие", reply_markup=global_keyboards.user_buttons))
    await state.set_state(GlobalStates.main)
        
@router.message(Command('admin'))
async def admin(message: Message, state: FSMContext):
    await message.delete()
    if message.from_user.id in await rq.get_admins():
        data = await state.get_data()
        await state.clear()
        try:
            await data['main_message'].edit_text('Админ функции', reply_markup=global_keyboards.admin_buttons))
        except:
            await state.update_data(main_message = await message.answer('Админ функции', reply_markup=global_keyboards.admin_buttons))
        await state.set_state(GlobalStates.admin)
        
"""

    (target_dir / "commands" / "commands.py").write_text(content)

def create_commands_keyboards(target_dir: Path):
    content = """from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder"""

def create_commands_states(target_dir: Path):
    content = """from aiogram.fsm.state import StatesGroup, State
    
class States(StatesGroup):
    pass"""

    (target_dir / "commands" / "commands_states.py").write_text(content)

def create_commands(target_dir: Path):
    create_commands_handler(target_dir)
    create_commands_keyboards(target_dir)
    create_commands_states(target_dir)

def create_global_states(target_dir: Path):
    content = """from aiogram.fsm.state import StatesGroup, State
    
class GlobalStates(StatesGroup):
    main = State()
    admin = State()    
"""

    (target_dir / "global_states.py").write_text(content)

def create_global_keyboards(target_dir: Path):
    content = """from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton)
                            
admin_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [

        ]
    ]
)

user_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [

        ]
    ]
    
)

def count(n):
    keyboard = InlineKeyboardBuilder()
    for i in range(n):

        keyboard.add(InlineKeyboardButton(text=f"{i+1}", callback_data=f"{i}"))
    keyboard.adjust(5)
    return keyboard.as_markup()


comfirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text = 'Подтвердить', callback_data='comfirm'),
            InlineKeyboardButton(text='Отменить', callback_data='cancel')
        ]
    ]
)

def time_hours():
    keyboard = InlineKeyboardBuilder()
    for i in range(24):
        keyboard.add(InlineKeyboardButton(text=f'{i}', callback_data=f'{i}'))
    return keyboard.adjust(4).as_markup()

def time_minutes():
    keyboard = InlineKeyboardBuilder()
    for i in range(0, 60, 15):
        if i == 0:
            keyboard.add(InlineKeyboardButton(text=f'00', callback_data=f'00'))
        else:
            keyboard.add(InlineKeyboardButton(text=f'{i}', callback_data=f'{i}'))
    return keyboard.adjust(4).as_markup()
    
                            
    """

    (target_dir / "global_keyboards.py").write_text(content)

def create_models(target_dir: Path):
    content = """ffrom sqlalchemy import BigInteger, String, ForeignKey, BLOB, INTEGER

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.db')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)"""

    (target_dir / "api" / "database" / "models.py").write_text(content)


def create_requests(target_dir: Path):
    content = """from api.database.models import async_session
from api.database.models import Event, Participant, Notifiticatoin, Admin
from sqlalchemy import select, update, delete

async def get_admins():
    admins = []
    async with async_session() as session:
        for admin in await session.scalars(select(Admin)):
            admins.append(admin)
    return admins"""

def create_database(target_dir: Path):
    create_models(target_dir)
    create_requests(target_dir)
