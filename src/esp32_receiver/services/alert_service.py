import httpx
import asyncio
from src.esp32_receiver.core.config import settings

async def send_alert_api_background():
    payload = {
        "event": "phone_usage_alert",
        "message": f"Person detected using a mobile phone continuously for over {settings.PHONE_USAGE_THRESHOLD_SECONDS // 60} minutes."
    }
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                print(f"[ALERT] Sending API alert (Attempt {attempt + 1}/3) to {settings.ALERT_API_URL}...")
                response = await client.post(settings.ALERT_API_URL, json=payload, timeout=5.0)
                if response.status_code in (200, 201):
                    print(f"[ALERT] Successfully sent API alert! Status: {response.status_code}")
                    return
                else:
                    print(f"[ALERT ERROR] API returned status {response.status_code}")
            except Exception as e:
                print(f"[ALERT ERROR] Attempt {attempt + 1} failed: {e}")
            
            if attempt < 2:
                await asyncio.sleep(2)
                
        print("[ALERT ERROR] Failed to send API alert after 3 attempts.")
