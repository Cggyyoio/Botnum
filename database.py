import aiosqlite
import asyncio

DB_PATH = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_string TEXT NOT NULL,
                country_code TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                assigned_to INTEGER DEFAULT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0.0,
                username TEXT
            )
        """)
        await db.commit()

async def add_session(session_string: str, country_code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO sessions (session_string, country_code) VALUES (?, ?)",
            (session_string, country_code)
        )
        await db.commit()

async def get_available_session(country_code: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if country_code:
            cursor = await db.execute(
                "SELECT * FROM sessions WHERE status='available' AND country_code=? LIMIT 1",
                (country_code,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM sessions WHERE status='available' LIMIT 1"
            )
        return await cursor.fetchone()

async def assign_session(session_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE sessions SET status='assigned', assigned_to=? WHERE id=?",
            (user_id, session_id)
        )
        await db.commit()

async def release_session(session_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE sessions SET status='available', assigned_to=NULL WHERE id=?",
            (session_id,)
        )
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,)
        )
        return await cursor.fetchone()

async def ensure_user(user_id: int, username: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()

async def update_balance(user_id: int, amount: float):
    """amount سالب = خصم، موجب = إضافة"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id=?",
            (amount, user_id)
        )
        await db.commit()