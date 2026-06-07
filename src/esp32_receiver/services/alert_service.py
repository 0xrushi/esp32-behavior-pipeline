import httpx
import asyncio
import hashlib
import hmac
import json
import uuid
from src.esp32_receiver.core.config import settings

async def send_alert_api_background():
    payload = {
        "event_type": "phone_usage_alert",
        "message": f"Person detected using a mobile phone continuously for over {settings.PHONE_USAGE_THRESHOLD_SECONDS // 60} minutes."
    }
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = {"Content-Type": "application/json", "X-Request-ID": str(uuid.uuid4())}
    if settings.ALERT_API_SECRET:
        signature = hmac.new(settings.ALERT_API_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
        headers["X-Webhook-Signature"] = signature

    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                print(f"[ALERT] Sending API alert (Attempt {attempt + 1}/3) to {settings.ALERT_API_URL}...")
                response = await client.post(settings.ALERT_API_URL, content=body, headers=headers, timeout=5.0)
                if response.status_code in (200, 201, 202):
                    print(f"[ALERT] Successfully sent API alert! Status: {response.status_code}")
                    return
                else:
                    print(f"[ALERT ERROR] API returned status {response.status_code}")
            except Exception as e:
                print(f"[ALERT ERROR] Attempt {attempt + 1} failed: {e}")
            
            if attempt < 2:
                await asyncio.sleep(2)
                
        print("[ALERT ERROR] Failed to send API alert after 3 attempts.")
