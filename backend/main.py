
import uuid
import logging

from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from starlette.concurrency import run_in_threadpool

from detector import detect_people
from video_processor import detect_people_video


# ------------------------------------
# CONFIGURATION
# ------------------------------------

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("CrowdVisionAI")


# ------------------------------------
# FASTAPI APPLICATION
# ------------------------------------

app = FastAPI(
    title="CrowdVision AI",
    description="AI-powered Crowd Detection System",
    version="1.0"
)


# ------------------------------------
# CORS CONFIGURATION
# ------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ------------------------------------
# SERVE OUTPUT IMAGES AND VIDEOS
# ------------------------------------

app.mount(
    "/outputs",
    StaticFiles(directory=str(OUTPUT_DIR)),
    name="outputs"
)


# ------------------------------------
# HOME
# ------------------------------------

@app.get("/")
def home():

    return {
        "message": "CrowdVision AI Backend",
        "status": "online"
    }


# ------------------------------------
# HEALTH CHECK
# ------------------------------------

@app.get("/health")
def health():

    return {
        "status": "online"
    }


# ------------------------------------
# IMAGE DETECTION
# ------------------------------------

@app.post("/detect/image")
async def image_detection(file: UploadFile = File(...)):

    allowed_extensions = [".jpg", ".jpeg", ".png"]

    extension = Path(file.filename or "").suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG and PNG are supported"
        )

    input_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{extension}"

    try:

        content = await file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty"
            )

        if len(content) > 20 * 1024 * 1024:

            raise HTTPException(
                status_code=413,
                detail="Image exceeds 20 MB"
            )

        input_path.write_bytes(content)

        logger.info("Starting image detection")

        # Call existing image detector
        result = await run_in_threadpool(
            detect_people,
            str(input_path)
        )

        output_path = Path(result["output_path"])

        if not output_path.exists():

            raise RuntimeError(
                "Detected image was not generated"
            )

        logger.info(
            "Image detection completed. People: %s",
            result["person_count"]
        )

        return {
            "success": True,
            "person_count": result["person_count"],
            "output_image": f"/outputs/{output_path.name}"
        }

    except HTTPException:
        raise

    except Exception as error:

        logger.exception("Image detection failed")

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        await file.close()

        if input_path.exists():
            input_path.unlink()


# ------------------------------------
# VIDEO DETECTION
# ------------------------------------

@app.post("/detect/video")
async def video_detection(file: UploadFile = File(...)):

    allowed_extensions = [".mp4", ".avi", ".mov"]

    extension = Path(file.filename or "").suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only MP4, AVI and MOV videos are supported"
        )

    input_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{extension}"

    try:

        content = await file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded video is empty"
            )

        if len(content) > 100 * 1024 * 1024:

            raise HTTPException(
                status_code=413,
                detail="Video exceeds 100 MB"
            )

        input_path.write_bytes(content)

        logger.info("Starting video detection")

        # Call existing video processor
        result = await run_in_threadpool(
            detect_people_video,
            str(input_path)
        )

        output_path = Path(result["output_path"])

        if not output_path.exists() or output_path.stat().st_size == 0:

            raise RuntimeError(
                "Processed video was not generated"
            )

        logger.info(
            "Video detection completed. Frames: %s",
            result["processed_frames"]
        )

        return {
            "success": True,
            "message": "Video detection completed",
            "unique_person_count": result["unique_person_count"],
            "max_people_in_frame": result["max_people_in_frame"],
            "average_people_per_frame": result["average_people_per_frame"],
            "processed_frames": result["processed_frames"],
            "output_video": f"/outputs/{output_path.name}"
        }

    except HTTPException:
        raise

    except Exception as error:

        logger.exception("Video detection failed")

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        await file.close()

        if input_path.exists():
            input_path.unlink()
