
import uuid
import logging

from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from starlette.concurrency import run_in_threadpool

from detector import detect_people
from person_matcher import (
    find_matching_person,
    find_matching_person_in_video
)
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
# REFERENCE-PHOTO PERSON MATCHING
# ------------------------------------

@app.post("/detect/person-match")
async def person_match_detection(
    group_image: UploadFile = File(...),
    reference_image: UploadFile = File(...)
):

    allowed_extensions = {".jpg", ".jpeg", ".png"}
    group_extension = Path(group_image.filename or "").suffix.lower()
    reference_extension = Path(reference_image.filename or "").suffix.lower()
    group_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{group_extension}"
    reference_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{reference_extension}"

    try:
        if group_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="The group image must be JPG, JPEG or PNG"
            )

        if reference_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="The reference photo must be JPG, JPEG or PNG"
            )

        group_content = await group_image.read()
        reference_content = await reference_image.read()

        if not group_content or not reference_content:
            raise HTTPException(
                status_code=400,
                detail="Both images must contain data"
            )

        if len(group_content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Group image exceeds 20 MB"
            )

        if len(reference_content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Reference photo exceeds 20 MB"
            )

        group_path.write_bytes(group_content)
        reference_path.write_bytes(reference_content)

        result = await run_in_threadpool(
            find_matching_person,
            str(group_path),
            str(reference_path)
        )
        output_path = Path(result["output_path"])

        if not output_path.exists():
            raise RuntimeError("Person-matching image was not generated")

        return {
            "success": True,
            "matched_count": result["matched_count"],
            "faces_found": result["faces_found"],
            "output_image": f"/outputs/{output_path.name}"
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        logger.exception("Reference-photo matching failed")
        raise HTTPException(status_code=500, detail=str(error))

    finally:
        await group_image.close()
        await reference_image.close()

        if group_path.exists():
            group_path.unlink()

        if reference_path.exists():
            reference_path.unlink()


@app.post("/detect/person-match/video")
async def person_match_video_detection(
    file: UploadFile = File(...),
    reference_image: UploadFile = File(...)
):

    video_extension = Path(file.filename or "").suffix.lower()
    reference_extension = Path(reference_image.filename or "").suffix.lower()
    video_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{video_extension}"
    reference_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{reference_extension}"

    try:
        if video_extension not in {".mp4", ".avi", ".mov"}:
            raise HTTPException(
                status_code=400,
                detail="Video must be MP4, AVI or MOV"
            )

        if reference_extension not in {".jpg", ".jpeg", ".png"}:
            raise HTTPException(
                status_code=400,
                detail="Reference photo must be JPG, JPEG or PNG"
            )

        video_content = await file.read()
        reference_content = await reference_image.read()

        if not video_content or not reference_content:
            raise HTTPException(
                status_code=400,
                detail="Both the video and reference photo must contain data"
            )

        if len(video_content) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Video exceeds 100 MB"
            )

        if len(reference_content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Reference photo exceeds 20 MB"
            )

        video_path.write_bytes(video_content)
        reference_path.write_bytes(reference_content)

        result = await run_in_threadpool(
            find_matching_person_in_video,
            str(video_path),
            str(reference_path)
        )
        output_path = Path(result["output_path"])

        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise RuntimeError("Person-matching video was not generated")

        return {
            "success": True,
            "matched_frames": result["matched_frames"],
            "max_matches_in_frame": result["max_matches_in_frame"],
            "processed_frames": result["processed_frames"],
            "output_video": f"/outputs/{output_path.name}"
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        logger.exception("Reference-photo video matching failed")
        raise HTTPException(status_code=500, detail=str(error))

    finally:
        await file.close()
        await reference_image.close()

        if video_path.exists():
            video_path.unlink()

        if reference_path.exists():
            reference_path.unlink()


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
