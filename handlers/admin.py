from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_session
from config import ADMIN_IDS

router = Router()
router.message.filter(F.from_user.id.in_(ADMIN_IDS))

class AddSessionState(StatesGroup):
    waiting_for_string = State()
    waiting_for_country = State()

_temp_session = {}  # تخزين مؤقت بين الخطوات

@router.message(Command("add_session"))
async def cmd_add_session(message: Message, state: FSMContext):
    await message.answer("أرسل الـ Session String:")
    await state.set_state(AddSessionState.waiting_for_string)

@router.message(AddSessionState.waiting_for_string)
async def process_session_string(message: Message, state: FSMContext):
    await state.update_data(session_string=message.text.strip())
    await message.answer("أرسل كود الدولة (مثال: EG, SA, US):")
    await state.set_state(AddSessionState.waiting_for_country)

@router.message(AddSessionState.waiting_for_country)
async def process_country_code(message: Message, state: FSMContext):
    data = await state.get_data()
    country = message.text.strip().upper()

    await add_session(data["session_string"], country)
    await message.answer(f"✅ تم إضافة الـ Session بنجاح\nالدولة: {country}")
    await state.clear()

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    from database import DB_PATH
    import aiosqlite
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM sessions WHERE status='available'")
        available = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM sessions WHERE status='assigned'")
        assigned = (await cur.fetchone())[0]

    await message.answer(
        f"📊 إحصائيات\n"
        f"متاح: {available}\n"
        f"مُسند: {assigned}"
    )