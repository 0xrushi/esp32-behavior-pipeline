# ESP32 Receiver

This project is a high-performance, asynchronous FastAPI application that receives images from an ESP32 camera, analyzes them using an Object Detection Model (`RFDETRMedium`), and records whether a person is using a mobile phone. If a person uses a phone continuously for 5 minutes, it triggers an external API alert webhook.

## Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) package manager (recommended)
- CUDA-compatible GPU (optional, but highly recommended for fast inference)

## Configuration

All configurable settings are managed via `.env` using **Pydantic Settings**.

1. Open the `.env` file in the root directory (use `.env.example` as a template).
2. Edit the following variables as needed:
   - `ALERT_API_URL`: The webhook URL for alerts.
   - `PORT`: The port the server listens on.

## Installation

To install the dependencies and the project:

```bash
uv sync
```

## Running the Application

To start the receiver server:

```bash
uv run esp32-receiver
```

The server will automatically load the model, initialize the local SQLite database (`camera_events.db`), and start listening for POST requests on `http://0.0.0.0:8000/frame`.

## Project Structure

- `src/esp32_receiver/api/`: FastAPI routes.
- `src/esp32_receiver/core/`: Configuration with Pydantic Settings.
- `src/esp32_receiver/database/`: Database management.
- `src/esp32_receiver/models/`: AI model logic.
- `src/esp32_receiver/services/`: Business logic and background tasks.

## Testing

Run integration tests with:

```bash
uv run pytest -v tests/test_integration.py
```

## API Endpoints

- **`POST /frame`**: Expects raw JPEG image bytes. Analyzes and stores the results.
- **`GET /ping`**: Health check.
- **`GET /recent?limit=20`**: Returns recent detections.
- **`GET /stats`**: Returns summary analytics.
