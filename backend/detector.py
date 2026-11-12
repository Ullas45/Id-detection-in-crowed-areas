
from ultralytics import YOLO
import cv2
import os

# =====================================
# 1. LOAD YOLO11 MODEL
# =====================================

model = YOLO("yolo11n.pt")


# =====================================
# 2. PERSON DETECTION FUNCTION
# =====================================

def detect_people(image_path):

    # Read input image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    # Run improved YOLO detection
    results = model.predict(
        source=image,
        conf=0.20,
        imgsz=1280,
        max_det=500,
        classes=[0],
        iou=0.45,
        agnostic_nms=True,
        verbose=False
    )

    person_count = 0

    # Process detection results
    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])

            # COCO class 0 = Person
            if class_id == 0:

                person_count += 1

                # Bounding box coordinates
                x1, y1, x2, y2 = map(
                    int, box.xyxy[0]
                )

                # Confidence score
                confidence = float(box.conf[0])

                # Draw bounding box
                cv2.rectangle(
                    image,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                # Display person label
                cv2.putText(
                    image,
                    f"Person {confidence:.2f}",
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

    # =====================================
    # 3. SAVE DETECTED IMAGE
    # =====================================

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    output_dir = os.path.join(
        base_dir,
        "outputs"
    )

    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(
        output_dir,
        "detected_image.jpg"
    )

    success = cv2.imwrite(
        output_path,
        image
    )

    if not success:
        raise RuntimeError("Unable to save output image")

    # =====================================
    # 4. RETURN RESULTS
    # =====================================

    return {
        "person_count": person_count,
        "output_path": output_path
    }


# =====================================
# 5. MAIN PROGRAM
# =====================================

if __name__ == "__main__":

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    # Input image
    image_path = os.path.join(
        base_dir,
        "crowd.png"
    )

    print("Starting CrowdVision AI...")
    print("Input Image:", image_path)

    if not os.path.exists(image_path):
        print("ERROR: crowd.png not found!")
    else:

        result = detect_people(image_path)

        print("\n========== DETECTION RESULTS ==========")

        print(
            "Total People Detected:",
            result["person_count"]
        )

        print(
            "Output Image:",
            result["output_path"]
        )

        print("=======================================")
        print("Detection Completed Successfully!")
