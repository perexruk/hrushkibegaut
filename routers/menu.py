import random
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import LOVED_USER_ID
from data.photos import photos
from data.notes import notes
from data.memes import memes

router = Router()

# FSM состояния
class MenuState(StatesGroup):
    main = State()
    photos = State()
    notes = State()
    memes = State()

# ---------- Универсальное хранилище очередей ----------
user_media_state = {}
# {
#   user_id: {
#       "photos": {"queue": [...], "total": int, "index": int},
#       "notes":  {"queue": [...], "total": int, "index": int},
#       "memes":  {"queue": [...], "total": int, "index": int},
#   }
# }

def get_next_item(user_id: int, items: list, section: str):
    if not items:
        return None, 0, 0

    if user_id not in user_media_state:
        user_media_state[user_id] = {}

    if (
        section not in user_media_state[user_id]
        or not user_media_state[user_id][section]["queue"]
    ):
        shuffled = items.copy()
        random.shuffle(shuffled)

        user_media_state[user_id][section] = {
            "queue": shuffled,
            "total": len(shuffled),
            "index": 0,
        }

    state = user_media_state[user_id][section]

    item = state["queue"].pop()
    state["index"] += 1

    return item, state["index"], state["total"]

# ---------- Inline-кнопки ----------
main_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🐽 Двоесашие", callback_data="photos")],
        [InlineKeyboardButton(text="68 Причин Почему Я Люблю Тебя", callback_data="notes")],
        [InlineKeyboardButton(text="💅 Мы в мемах", callback_data="memes")],
    ]
)

# ---------- Reply-клавиатура для фото ----------
photo_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Давай ещё фоточку")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True
)

# ---------- Reply-клавиатура для причин ----------
note_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Ещё одна причина")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True
)

# ---------- Reply-клавиатура для мемов ----------
meme_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Реально мы")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True
)

# ---------- /start ----------
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(MenuState.main)

    await message.answer("1... 4... 8... 8... 🥥🍉")

    await message.answer(
        "Привит, Сашка 🐒\n\n"
        "Я создала етого горе-бота, чтобы нестандартным способом поздравить тебя, а также просто выразить через него свои чувства, кек"
    )

    await message.answer(
        "Выбирай",
        reply_markup=main_keyboard
    )

# ---------- Кнопка «Двоесашие» ----------
@router.callback_query(F.data == "photos")
async def photos_handler(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != LOVED_USER_ID:
        await callback.answer()
        return
    
    await state.set_state(MenuState.photos)

    await callback.message.answer("🤝 Переходим в раздел «Двоесашие»")

    photo, index, total = get_next_item(
        callback.from_user.id,
        photos,
        "photos"
    )

    try:
        await callback.message.answer_photo(
            photo,
            caption=f"Фото {index} из {total}",
            reply_markup=photo_keyboard
        )
    except TelegramBadRequest:
        await callback.message.answer("Ошибка с фото. Проверь file_id.")

    await callback.answer()

# ---------- Ещё фото ----------
@router.message(F.text == "Давай ещё фоточку")
async def more_photos(message: Message):
    photo, index, total = get_next_item(
        message.from_user.id,
        photos,
        "photos"
    )

    try:
        await message.answer_photo(
            photo,
            caption=f"Фото {index} из {total}",
            reply_markup=photo_keyboard
        )
    except TelegramBadRequest:
        await message.answer("Ошибка с фото. Проверь file_id.")

# ---------- Кнопка «Причины» ----------
@router.callback_query(F.data == "notes")
async def notes_handler(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != LOVED_USER_ID:
        await callback.answer()
        return
    
    await state.set_state(MenuState.notes)

    await callback.message.answer("🤝 Переходим в раздел «Чому я тебе кохаю»")

    note, index, total = get_next_item(
        callback.from_user.id,
        notes,
        "notes"
    )

    await callback.message.answer(
        f"{note}\n\nПричина {index} из {total}",
        reply_markup=note_keyboard
    )

    await callback.answer()

# ---------- Ещё причины ----------
@router.message(F.text == "Ещё одна причина")
async def more_notes(message: Message):
    note, index, total = get_next_item(
        message.from_user.id,
        notes,
        "notes"
    )

    await message.answer(
        f"{note}\n\nПричина {index} из {total}",
        reply_markup=note_keyboard
    )

# ---------- Кнопка «Мы в мемах» ----------
@router.callback_query(F.data == "memes")
async def memes_handler(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != LOVED_USER_ID:
        await callback.answer()
        return
    
    await state.set_state(MenuState.memes)

    await callback.message.answer("🤝 Переходим в раздел «ЯМЫ Мемы»")

    meme, index, total = get_next_item(
        callback.from_user.id,
        memes,
        "memes"
    )

    try:
        await callback.message.answer_photo(
        meme,
        caption=f"Мем {index} из {total}",
        reply_markup=meme_keyboard
        )
    except TelegramBadRequest:
        await callback.message.answer("Ошибка с фото.")

    await callback.answer()

# ---------- Ещё мемы ----------
@router.message(F.text == "Реально мы")
async def more_memes(message: Message):
    meme, index, total = get_next_item(
        message.from_user.id,
        memes,
        "memes"
    )

    try:
        await message.answer_photo(
            meme,
            caption=f"Мем {index} из {total}",
            reply_markup=meme_keyboard
        )
    except TelegramBadRequest:
        await message.answer("Ошибка с фото. Проверь file_id.")

# ---------- Назад ----------
@router.message(F.text == "Назад")
async def back_handler(message: Message, state: FSMContext):
    await state.set_state(MenuState.main)

    await message.answer(
        "↩ Повертаємося в головне меню 🇺🇦",
        reply_markup=ReplyKeyboardRemove()
    )

    await message.answer(
        "Выбери раздел",
        reply_markup=main_keyboard
    )

# ---------- Скрытые фразы ----------
@router.message(F.text == "Хрю")
async def secret_handler(message: Message):
    if message.from_user.id == LOVED_USER_ID:
        await message.answer(
            "- После стольких лет?\n"
            "- Всегда хрю."
        )

@router.message(F.text == "Слава Украине")
async def secret_handler(message: Message):
    if message.from_user.id == LOVED_USER_ID:
        await message.answer(
            "Ще не вмерла України ні слава, ні воля,\n"
            "Ще нам, браття-українці, усміхнеться доля.\n"
            "Згинуть наші вороженьки, як роса на сонці,\n"
            "Запануєм і ми, браття, у своїй сторонці.\n"
            "Душу й тіло ми положим за нашу свободу,\n"
            "І покажем, що ми, браття, козацького роду.\n"
            "Станем, браття, в бій кривавий, від Сяну до Дону,\n"
            "В ріднім краю панувати не дамо нікому.\n"
            "Чорне море ще всміхнеться, дід Дніпро зрадіє,\n"
            "Ще на нашій Україні доленька наспіє.\n"
            "А завзяття, праця щира свого ще докаже,\n"
            "Ще ся волі в Україні піснь гучна розляже\n"
            "За Карпати відіб’ється, згомонить степами,\n"
            "України слава стане поміж народами\n"
        )