
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from detector import detect_people

import os
import uuid
import shutil


# =====================================
# 1. CREATE FASTAPI APPLICATION
# =====================================

app = FastAPI(
    title="CrowdVision AI",
    description="AI Based Crowd Person Detection System",
    version="1.0"
)


# =====================================
# 2. ENABLE CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# 3. CREATE DIRECTORIES
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Serve processed images
app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUT_DIR),
    name="outputs"
)


# =====================================
# 4. HOME API
# =====================================

@app.get("/")
def home():

    return {
        "message": "Welcome to CrowdVision AI",
        "status": "Backend Running"
    }


# =====================================
# 5. HEALTH CHECK API
# =====================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "project": "CrowdVision AI"
    }


# =====================================
# 6. IMAGE DETECTION API
# =====================================

@app.post("/detect/image")
async def detect_image(file: UploadFile = File(...)):

    allowed_types = {
        "image/jpeg",
        "image/png"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported"
        )

    # Create unique filename
    extension = os.path.splitext(file.filename or "")[1].lower()

    if extension not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid image extension"
        )

    filename = f"{uuid.uuid4()}{extension}"

    input_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    try:

        # Save uploaded image
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty"
            )

        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Image must be smaller than 20 MB"
            )

        with open(input_path, "wb") as f:
            f.write(content)

        # Run YOLO detection
        result = detect_people(input_path)

        output_filename = os.path.basename(
            result["output_path"]
        )

        return {
            "success": True,
            "message": "Detection completed",
            "person_count": result["person_count"],
            "output_image": f"/outputs/{output_filename}"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(input_path):
            os.remove(input_path)
