import io
import sqlite3
import os
from PIL import Image
from fastapi.testclient import TestClient

from src.esp32_receiver.main import app
from src.esp32_receiver.core.config import settings

def test_frame_integration():
    # Delete DB if exists for clean test
    if settings.DB_PATH.exists():
        settings.DB_PATH.unlink()

    with TestClient(app) as client:
        # Create a dummy solid red image in memory
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        # 1. Post the image to the /frame endpoint
        response = client.post("/frame", content=img_bytes)
        
        # Verify the API response
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "filepath" in data
        assert "output_filepath" in data
        assert "answer" in data
        assert "cumulated_time" in data
        
        filepath = data["filepath"]
        output_filepath = data["output_filepath"]
        answer = data["answer"]
        notes = data["notes"]
        
        print(f"\n--- Model Answer on Dummy Image ---")
        print(f"Answer (Boolean): {answer}")
        print(f"Notes (Text): {notes}")
        print(f"Filepath: {filepath}")
        print(f"Output Filepath: {output_filepath}")
        print(f"-----------------------------------\n")

        # 2. Check the /recent API endpoint to see if it was saved
        recent_response = client.get("/recent?limit=1")
        assert recent_response.status_code == 200
        recent_data = recent_response.json()
        
        assert len(recent_data) > 0
        latest_record = recent_data[0]
        
        # Assert the DB record matches the API response
        assert latest_record["filepath"] == filepath
        assert latest_record["output_filepath"] == output_filepath
        assert latest_record["answer"] == answer

        # 3. Double-check directly inside the SQLite database
        with sqlite3.connect(settings.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM frames ORDER BY id DESC LIMIT 1").fetchone()
            assert row is not None
            assert row["filepath"] == filepath
            assert row["output_filepath"] == output_filepath
            assert row["answer"] == answer
