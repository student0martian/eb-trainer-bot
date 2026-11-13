from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.loader import get_ticket_ids

router = Router()


def tickets_keyboard():
    builder = InlineKeyboardBuilder()
    for ticket_id in get_ticket_ids():
        builder.button(text=str(ticket_id), callback_data=f"ticket:{ticket_id}")
    builder.adjust(5)
    return builder.as_markup()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Выберите тест:", reply_markup=tickets_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("/start — список тестов")
