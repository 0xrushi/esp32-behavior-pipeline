import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from src.esp32_receiver.core.config import settings
from src.esp32_receiver.database.manager import write_db, get_recent_frames, get_stats
from src.esp32_receiver.models.detector import detector
from src.esp32_receiver.services.alert_service import send_alert_api_background
from src.esp32_receiver.services.usage_tracker import tracker

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"status": "ok"}

@router.post("/frame")
async def receive_frame(request: Request, background_tasks: BackgroundTasks):
    image_bytes = await request.body()

    if not image_bytes:
        return JSONResponse({"ok": False, "error": "No image bytes received"}, status_code=400)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
    filepath = settings.FRAME_DIR / filename
    output_filepath = settings.OUTPUT_DIR / filename

    # Save original received JPEG in a thread since it's File I/O
    await asyncio.to_thread(filepath.write_bytes, image_bytes)

    # Run the heavy CPU-bound inference in a separate thread
    answer, notes, cumulated_time = await asyncio.to_thread(
        detector.analyze_frame, str(filepath), str(output_filepath)
    )

    # Update tracker and trigger alert if needed
    if await tracker.update(answer):
        background_tasks.add_task(send_alert_api_background)

    await write_db(
        filepath=str(filepath),
        output_filepath=str(output_filepath),
        answer=answer,
        cumulated_time=cumulated_time,
        notes=notes
    )

    state_str = "ON_PHONE" if answer else "NO_PHONE"
    streak_str = tracker.get_streak_info()

    print(
        f"[FRAME] {filepath} | "
        f"answer={answer} ({state_str}, streak={streak_str}) | "
        f"time={cumulated_time:.3f}s | "
        f"notes={notes}"
    )

    return {
        "ok": True,
        "filepath": str(filepath),
        "output_filepath": str(output_filepath),
        "answer": answer,
        "cumulated_time": cumulated_time,
        "notes": notes
    }

@router.get("/recent")
async def recent(limit: int = 20):
    return await get_recent_frames(limit)

@router.get("/stats")
async def stats():
    return await get_stats()
