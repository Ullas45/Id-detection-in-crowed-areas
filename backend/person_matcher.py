import uuid
from pathlib import Path
from threading import Lock

import cv2
import imageio_ffmpeg


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"
FACE_MATCH_THRESHOLD = 0.363

face_detector = None
face_recognizer = None
face_model_lock = Lock()


def _load_models():
    global face_detector, face_recognizer

    detector_path = MODEL_DIR / "face_detection_yunet_2026may.onnx"
    recognizer_path = MODEL_DIR / "face_recognition_sface_2021dec.onnx"

    if not detector_path.is_file() or not recognizer_path.is_file():
        raise FileNotFoundError(
            "Face-matching model files are missing from backend/models"
        )

    face_detector = cv2.FaceDetectorYN.create(
        str(detector_path),
        "",
        (320, 320),
        0.8,
        0.3,
        5000
    )
    face_recognizer = cv2.FaceRecognizerSF.create(
        str(recognizer_path),
        ""
    )


def _detect_faces(image):
    face_detector.setInputSize((image.shape[1], image.shape[0]))
    _, faces = face_detector.detect(image)
    return faces


def find_matching_person(group_image_path, reference_image_path):
    group_image = cv2.imread(str(group_image_path))
    reference_image = cv2.imread(str(reference_image_path))

    if group_image is None:
        raise ValueError("Unable to read the group image")

    if reference_image is None:
        raise ValueError("Unable to read the reference photo")

    with face_model_lock:
        if face_detector is None or face_recognizer is None:
            _load_models()

        reference_faces = _detect_faces(reference_image)

        if reference_faces is None or len(reference_faces) == 0:
            raise ValueError(
                "No face was found in the reference photo. "
                "Use a clear photo with one visible face."
            )

        if len(reference_faces) != 1:
            raise ValueError(
                "The reference photo must contain exactly one visible face."
            )

        reference_face = face_recognizer.alignCrop(
            reference_image,
            reference_faces[0]
        )
        reference_features = face_recognizer.feature(reference_face)
        group_faces = _detect_faces(group_image)

        matched_count = 0

        if group_faces is not None:
            for face in group_faces:
                aligned_face = face_recognizer.alignCrop(group_image, face)
                features = face_recognizer.feature(aligned_face)
                similarity = face_recognizer.match(
                    reference_features,
                    features,
                    cv2.FaceRecognizerSF_FR_COSINE
                )

                if similarity < FACE_MATCH_THRESHOLD:
                    continue

                x, y, width, height = map(int, face[:4])
                left = max(x, 0)
                top = max(y, 0)
                right = min(x + width, group_image.shape[1])
                bottom = min(y + height, group_image.shape[0])

                cv2.rectangle(
                    group_image,
                    (left, top),
                    (right, bottom),
                    (0, 255, 0),
                    3
                )
                cv2.putText(
                    group_image,
                    f"Match {similarity:.2f}",
                    (left, max(top - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                matched_count += 1

    status = (
        f"Matching faces found: {matched_count}"
        if matched_count
        else "No matching face found"
    )
    cv2.rectangle(group_image, (10, 10), (520, 65), (0, 0, 0), -1)
    cv2.putText(
        group_image,
        status,
        (20, 48),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    output_path = BASE_DIR / "outputs" / f"person_match_{uuid.uuid4().hex}.jpg"
    if not cv2.imwrite(str(output_path), group_image):
        raise RuntimeError("Unable to save the person-matching result")

    return {
        "matched_count": matched_count,
        "faces_found": 0 if group_faces is None else len(group_faces),
        "output_path": str(output_path)
    }


def find_matching_person_in_video(video_path, reference_image_path):
    video_path = Path(video_path)
    reference_image = cv2.imread(str(reference_image_path))

    if not video_path.is_file():
        raise FileNotFoundError("Uploaded video was not found")

    if reference_image is None:
        raise ValueError("Unable to read the reference photo")

    output_path = BASE_DIR / "outputs" / f"person_match_{uuid.uuid4().hex}.mp4"
    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        raise ValueError("Unable to open uploaded video")

    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or fps > 120:
        fps = 25.0

    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if width <= 0 or height <= 0:
        capture.release()
        raise ValueError("Invalid video dimensions")

    output_width = width + width % 2
    output_height = height + height % 2
    writer = None
    processed_frames = 0
    matched_frames = 0
    max_matches_in_frame = 0

    try:
        with face_model_lock:
            if face_detector is None or face_recognizer is None:
                _load_models()

            reference_faces = _detect_faces(reference_image)
            if reference_faces is None or len(reference_faces) == 0:
                raise ValueError(
                    "No face was found in the reference photo. "
                    "Use a clear photo with one visible face."
                )

            if len(reference_faces) != 1:
                raise ValueError(
                    "The reference photo must contain exactly one visible face."
                )

            reference_face = face_recognizer.alignCrop(
                reference_image,
                reference_faces[0]
            )
            reference_features = face_recognizer.feature(reference_face)
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
            writer.send(None)

            while True:
                success, frame = capture.read()
                if not success:
                    break

                faces = _detect_faces(frame)
                frame_matches = 0

                if faces is not None:
                    for face in faces:
                        aligned_face = face_recognizer.alignCrop(frame, face)
                        features = face_recognizer.feature(aligned_face)
                        similarity = face_recognizer.match(
                            reference_features,
                            features,
                            cv2.FaceRecognizerSF_FR_COSINE
                        )

                        if similarity < FACE_MATCH_THRESHOLD:
                            continue

                        x, y, face_width, face_height = map(int, face[:4])
                        left = max(x, 0)
                        top = max(y, 0)
                        right = min(x + face_width, width)
                        bottom = min(y + face_height, height)
                        cv2.rectangle(
                            frame,
                            (left, top),
                            (right, bottom),
                            (0, 255, 0),
                            3
                        )
                        cv2.putText(
                            frame,
                            f"Match {similarity:.2f}",
                            (left, max(top - 10, 25)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
                        )
                        frame_matches += 1

                max_matches_in_frame = max(max_matches_in_frame, frame_matches)
                if frame_matches:
                    matched_frames += 1

                cv2.rectangle(frame, (10, 10), (520, 65), (0, 0, 0), -1)
                cv2.putText(
                    frame,
                    f"Matching faces: {frame_matches}",
                    (20, 48),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
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

                writer.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes())
                processed_frames += 1

        writer.close()
        writer = None

        if processed_frames == 0:
            raise ValueError("No frames extracted from video")

        if not output_path.is_file() or output_path.stat().st_size == 0:
            raise RuntimeError("Processed video was not generated")

        verification = cv2.VideoCapture(str(output_path))
        is_readable = verification.isOpened() and verification.read()[0]
        verification.release()
        if not is_readable:
            raise RuntimeError("Generated matching video cannot be opened")

        return {
            "output_path": str(output_path),
            "processed_frames": processed_frames,
            "matched_frames": matched_frames,
            "max_matches_in_frame": max_matches_in_frame
        }
    except Exception:
        if writer is not None:
            writer.close()
        if output_path.exists():
            output_path.unlink()
        raise
    finally:
        capture.release()
