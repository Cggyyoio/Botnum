import asyncio
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, FloodWait
from config import API_ID, API_HASH

async def get_latest_message_from_telegram(session_string: str) -> str | None:
    """
    تفتح الـ Session وتجلب آخر رسالة من Telegram الرسمي (777000)
    تُستدعى من داخل Aiogram handler بشكل async
    """
    client = Client(
        name="temp_session",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session_string,
        in_memory=True  # مهم: لا يحفظ ملفات على القرص
    )

    try:
        await client.start()

        messages = await client.get_messages(
            chat_id=777000,
            limit=1
        )

        if messages and messages[0].text:
            return messages[0].text
        return None

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return None
    except Exception as e:
        print(f"[SessionManager] Error: {e}")
        return None
    finally:
        # مهم جداً: إغلاق الـ client دائماً
        if client.is_connected:
            await client.stop()