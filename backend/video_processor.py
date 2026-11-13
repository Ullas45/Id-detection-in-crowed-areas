
import cv2
import imageio_ffmpeg
import uuid
from pathlib import Path
from threading import Lock
from ultralytics import YOLO

# ------------------------------------------------
# CONFIGURATION
# ------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = BASE_DIR / "yolo11n.pt"

if not MODEL_PATH.exists():
    MODEL_PATH = BASE_DIR.parent / "yolo11n.pt"

model = YOLO(str(MODEL_PATH))
model_lock = Lock()


# ------------------------------------------------
# VIDEO DETECTION
# ------------------------------------------------

def detect_people_video(video_path):

    video_path = Path(video_path)

    if not video_path.exists():
        raise FileNotFoundError("Uploaded video not found")

    video_id = uuid.uuid4().hex

    output_path = OUTPUT_DIR / f"detected_{video_id}.mp4"

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError("Cannot open uploaded video")

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0 or fps > 120:
        fps = 25.0

    unique_ids = set()
    total_people = 0
    max_people = 0
    processed_frames = 0

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if width <= 0 or height <= 0:
        cap.release()
        raise ValueError("Invalid video dimensions")

    print("Starting video detection...")
    print("Video FPS:", fps)
    print("Resolution:", width, "x", height)

    output_width = width + width % 2
    output_height = height + height % 2
    writer = imageio_ffmpeg.write_frames(
        str(output_path),
        size=(output_width, output_height),
        fps=fps,
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        codec="libx264",
        quality=8,
        macro_block_size=1,
        output_params=["-preset", "ultrafast", "-movflags", "+faststart"]
    )

    try:
        writer.send(None)

        while True:

            success, frame = cap.read()

            if not success:
                break

            # YOLO tracking
            with model_lock:

                results = model.track(
                    source=frame,
                    persist=True,
                    tracker="bytetrack.yaml",
                    conf=0.25,
                    imgsz=640,
                    classes=[0],
                    verbose=False
                )

            person_count = 0

            for result in results:

                if result.boxes is None:
                    continue

                boxes = result.boxes

                for index, box in enumerate(boxes):

                    if int(box.cls[0]) != 0:
                        continue

                    person_count += 1

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0].tolist()
                    )

                    confidence = float(box.conf[0])

                    track_id = None

                    if boxes.id is not None:
                        track_id = int(boxes.id[index])
                        unique_ids.add(track_id)

                    # Draw bounding box
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    label = (
                        f"Person {track_id} {confidence:.2f}"
                        if track_id is not None
                        else f"Person {confidence:.2f}"
                    )

                    cv2.putText(
                        frame,
                        label,
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

            total_people += person_count
            max_people = max(max_people, person_count)

            # Display count
            cv2.rectangle(
                frame,
                (10, 10),
                (330, 60),
                (0, 0, 0),
                -1
            )

            cv2.putText(
                frame,
                f"People Detected: {person_count}",
                (20, 43),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            if output_width != width or output_height != height:
                frame = cv2.copyMakeBorder(
                    frame,
                    0,
                    output_height - height,
                    0,
                    output_width - width,
                    cv2.BORDER_REPLICATE
                )

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            writer.send(rgb_frame.tobytes())

            processed_frames += 1

            if processed_frames % 30 == 0:
                print(
                    "Processed frames:",
                    processed_frames
                )

        cap.release()
        writer.close()
        writer = None

        if processed_frames == 0:
            raise ValueError("No frames extracted from video")

        print("All frames processed:", processed_frames)

        # ----------------------------------------
        # STEP 3: VERIFY OUTPUT VIDEO
        # ----------------------------------------

        if not output_path.exists():
            raise RuntimeError("Output video was not generated")

        if output_path.stat().st_size == 0:
            raise RuntimeError("Output video is empty")

        check = cv2.VideoCapture(str(output_path))

        if not check.isOpened():
            raise RuntimeError(
                "Generated video cannot be opened"
            )

        output_frame_count = int(
            check.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        check.release()

        if output_frame_count == 0:
            raise RuntimeError(
                "Generated video contains no frames"
            )

        print("--------------------------------")
        print("VIDEO GENERATION SUCCESSFUL")
        print("Output:", output_path)
        print("Frames:", output_frame_count)
        print("File size:", output_path.stat().st_size)
        print("--------------------------------")

        return {
            "output_path": str(output_path),
            "unique_person_count": len(unique_ids),
            "max_people_in_frame": max_people,
            "average_people_per_frame": round(
                total_people / processed_frames, 2
            ),
            "processed_frames": processed_frames
        }

    except Exception:

        cap.release()

        if writer is not None:
            writer.close()

        if output_path.exists():
            output_path.unlink()

        raise
