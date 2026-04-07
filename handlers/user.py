from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import (
    get_available_session, assign_session, release_session,
    get_user, ensure_user, update_balance
)
from session_manager import get_latest_message_from_telegram
from config import SESSION_PRICE

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await ensure_user(message.from_user.id, message.from_user.username)
    user = await get_user(message.from_user.id)
    balance = user[2] if user else 0.0

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔢 طلب رقم", callback_data="request_number")],
        [InlineKeyboardButton(text="💰 رصيدي", callback_data="my_balance")],
    ])
    await message.answer(
        f"مرحباً {message.from_user.first_name} 👋\n"
        f"رصيدك: {balance}",
        reply_markup=kb
    )

@router.callback_query(F.data == "my_balance")
async def cb_balance(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    balance = user[2] if user else 0.0
    await callback.answer(f"رصيدك: {balance}", show_alert=True)

@router.callback_query(F.data == "request_number")
async def cb_request_number(callback: CallbackQuery):
    user_id = callback.from_user.id
    await ensure_user(user_id)

    user = await get_user(user_id)
    balance = user[2] if user else 0.0

    if balance < SESSION_PRICE:
        await callback.answer(
            f"رصيد غير كافٍ. المطلوب: {SESSION_PRICE}",
            show_alert=True
        )
        return

    # سحب session متاح
    session_row = await get_available_session()
    if not session_row:
        await callback.answer("لا توجد أرقام متاحة حالياً", show_alert=True)
        return

    session_id = session_row[0]
    session_string = session_row[1]

    await callback.message.edit_text("⏳ جاري معالجة طلبك...")
    await assign_session(session_id, user_id)

    # ← هنا يتم استدعاء Pyrogram داخل Aiogram handler بشكل async
    result = await get_latest_message_from_telegram(session_string)

    if result:
        # خصم الرصيد فقط عند النجاح
        await update_balance(user_id, -SESSION_PRICE)
        await callback.message.edit_text(
            f"✅ تمت العملية بنجاح\n\n"
            f"📩 آخر رسالة:\n`{result}`\n\n"
            f"💰 تم خصم {SESSION_PRICE} من رصيدك",
            parse_mode="Markdown"
        )
    else:
        # فشل → إرجاع الـ session
        await release_session(session_id)
        await callback.message.edit_text("❌ فشلت العملية، لم يُخصم أي رصيد")