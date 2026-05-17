from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.esp32_receiver.api.routes import router
from src.esp32_receiver.database.manager import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(title="ESP32 Receiver", lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    from src.esp32_receiver.core.config import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
