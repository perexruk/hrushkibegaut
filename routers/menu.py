import random
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest

from config import LOVED_USER_ID
from data.photos import photos
from data.notes import notes

router = Router()

# ---------- Inline-кнопки ----------
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Мы", callback_data="we")],
        [InlineKeyboardButton(text="💌 Записка", callback_data="note")],
    ]
)

# ---------- /start ----------
@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Я храню кое-что важное.",
        reply_markup=keyboard
    )

# ---------- Кнопка «Мы» ----------
@router.callback_query(F.data == "we")
async def we_handler(callback: CallbackQuery):
    if callback.from_user.id != LOVED_USER_ID:
        await callback.message.answer("Эта кнопка доступна не всем.")
        await callback.answer()
        return

    photo = random.choice(photos)
    try:
        await callback.message.answer_photo(photo)
    except TelegramBadRequest:
        await callback.message.answer(
            "Произошла ошибка с фото. Проверьте, правильный ли file_id."
        )
    await callback.answer()

# ---------- Кнопка «Записка» ----------
@router.callback_query(F.data == "note")
async def note_handler(callback: CallbackQuery):
    if callback.from_user.id != LOVED_USER_ID:
        await callback.message.answer("Эта кнопка доступна не всем.")
        await callback.answer()
        return

    note = random.choice(notes)
    await callback.message.answer(note)
    await callback.answer()

# ---------- Скрытая фраза ----------
@router.message(F.text == "Я люблю тебя")
async def secret_handler(message: Message):
    if message.from_user.id == LOVED_USER_ID:
        await message.answer(
            "Я люблю тебя сильнее, чем можно выразить словами ❤️"
        )

# ---------- Временный handler для получения file_id ----------
# После того как получишь file_id, можно удалить этот обработчик
@router.message(F.photo)
async def get_file_id(message: Message):
    file_id = message.photo[-1].file_id
    await message.answer(f"FILE_ID: {file_id}")