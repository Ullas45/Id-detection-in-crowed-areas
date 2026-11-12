from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from detector import Detector
from tracker import Tracker


class VideoProcessor:
    def __init__(self, model_path: str | None = None) -> None:
        self.detector = Detector(model_path=model_path)
        self.tracker = Tracker()

    def process_video(self, input_path: str | Path, output_dir: str | Path) -> tuple[str, int]:
        source = Path(input_path)
        output_folder = Path(output_dir)
        output_folder.mkdir(parents=True, exist_ok=True)

        if not source.exists():
            raise FileNotFoundError(f"Input video not found: {source}")

        capture = cv2.VideoCapture(str(source))
        if not capture.isOpened():
            raise ValueError(f"Unable to open video: {source}")

        fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        output_path = output_folder / f"{source.stem}_processed.mp4"

        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )

        frames_processed = 0
        while True:
            success, frame = capture.read()
            if not success:
                break

            detections = self.detector.detect(frame)
            if not detections:
                detections = []

            tracked_objects = self.tracker.update(detections)
            for tracked in tracked_objects:
                x, y, w, h = [int(v) for v in tracked["bbox"]]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"ID: {tracked['id']}",
                    (x, max(y - 10, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            writer.write(frame)
            frames_processed += 1

        capture.release()
        writer.release()
        return str(output_path), frames_processed
