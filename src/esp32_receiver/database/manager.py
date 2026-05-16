import aiosqlite
from datetime import datetime
from src.esp32_receiver.core.config import settings

async def init_db():
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filepath TEXT NOT NULL,
                output_filepath TEXT NOT NULL,
                answer INTEGER NOT NULL,
                cumulated_time REAL NOT NULL,
                notes TEXT
            )
        """)
        await db.commit()

async def write_db(filepath: str, output_filepath: str, answer: bool, cumulated_time: float, notes: str):
    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute("""
            INSERT INTO frames (
                timestamp,
                filepath,
                output_filepath,
                answer,
                cumulated_time,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            filepath,
            output_filepath,
            int(answer),
            cumulated_time,
            notes
        ))
        await db.commit()

async def get_recent_frames(limit: int = 20):
    async with aiosqlite.connect(settings.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM frames ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_stats():
    async with aiosqlite.connect(settings.DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM frames") as cursor:
            total_frames = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM frames WHERE answer = 1") as cursor:
            positive_detections = (await cursor.fetchone())[0]
        return {
            "total_frames_analyzed": total_frames,
            "positive_phone_detections": positive_detections
        }
