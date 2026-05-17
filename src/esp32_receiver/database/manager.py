import asyncpg
from datetime import datetime
from src.esp32_receiver.core.config import settings

_pool: asyncpg.Pool | None = None


async def init_db():
    global _pool
    _pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=5)
    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS esp32_frames (
                id              SERIAL PRIMARY KEY,
                timestamp       TIMESTAMPTZ NOT NULL,
                filepath        TEXT NOT NULL,
                output_filepath TEXT NOT NULL,
                answer          BOOLEAN NOT NULL,
                cumulated_time  REAL NOT NULL,
                notes           TEXT
            )
        """)


async def close_db():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def write_db(filepath: str, output_filepath: str, answer: bool, cumulated_time: float, notes: str):
    async with _pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO esp32_frames (timestamp, filepath, output_filepath, answer, cumulated_time, notes)
            VALUES ($1, $2, $3, $4, $5, $6)
        """,
            datetime.now(),
            filepath,
            output_filepath,
            answer,
            cumulated_time,
            notes,
        )


async def get_recent_frames(limit: int = 20):
    async with _pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM esp32_frames ORDER BY id DESC LIMIT $1", limit
        )
        return [dict(r) for r in rows]


async def get_stats():
    async with _pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM esp32_frames")
        positive = await conn.fetchval("SELECT COUNT(*) FROM esp32_frames WHERE answer = true")
        return {
            "total_frames_analyzed": total,
            "positive_phone_detections": positive,
        }
