
import cv2
import uuid
from pathlib import Path
from threading import Lock
from ultralytics import YOLO

# -----------------------------------
# CONFIGURATION
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = BASE_DIR / "yolo11n.pt"

model = YOLO(str(MODEL_PATH))

# Prevent simultaneous model inference
model_lock = Lock()


# -----------------------------------
# IMAGE PERSON DETECTION
# -----------------------------------

def detect_people(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError("Unable to read uploaded image")

    print("Starting image detection...")

    # Run YOLO detection
    with model_lock:

        results = model.predict(
            source=image,
            conf=0.10,
            imgsz=640,
            max_det=500,
            classes=[0],
            iou=0.50,
            agnostic_nms=False,
            verbose=False
        )

    person_count = 0

    # Process detection results
    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])

            # COCO class 0 = Person
            if class_id != 0:
                continue

            person_count += 1

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            confidence = float(box.conf[0])

            # Draw bounding box
            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Person label
            label = f"Person {confidence:.2f}"

            cv2.putText(
                image,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

    # Display total people
    cv2.rectangle(
        image,
        (10, 10),
        (350, 60),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        image,
        f"Total People: {person_count}",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    # Save output
    output_filename = f"detected_{uuid.uuid4().hex}.jpg"

    output_path = OUTPUT_DIR / output_filename

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise RuntimeError("Unable to save detected image")

    print("Image detection completed")
    print("People detected:", person_count)
    print("Output:", output_path)

    return {
        "person_count": person_count,
        "output_path": str(output_path)
    }
