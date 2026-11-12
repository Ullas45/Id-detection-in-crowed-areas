from __future__ import annotations

from typing import Any


class Tracker:
    """A simple centroid-based tracker for assigning IDs to detected objects."""

    def __init__(self, max_disappeared: int = 10) -> None:
        self.max_disappeared = max_disappeared
        self.next_object_id = 0
        self.objects: dict[int, dict[str, Any]] = {}
        self.disappeared: dict[int, int] = {}

    def _centroid(self, bbox: list[int | float]) -> tuple[float, float]:
        x, y, w, h = bbox
        return (x + w / 2.0, y + h / 2.0)

    def update(self, detections: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not detections:
            for object_id in list(self.objects.keys()):
                self.disappeared[object_id] = self.disappeared.get(object_id, 0) + 1
                if self.disappeared[object_id] > self.max_disappeared:
                    del self.objects[object_id]
                    del self.disappeared[object_id]
            return []

        tracked = []
        for detection in detections:
            bbox = detection.get("bbox", [0, 0, 0, 0])
            cent = self._centroid(bbox)
            if not self.objects:
                object_id = self.next_object_id
                self.next_object_id += 1
                self.objects[object_id] = {"centroid": cent, "bbox": bbox}
                self.disappeared[object_id] = 0
                tracked.append({"id": object_id, "bbox": bbox, "centroid": cent})
                continue

            closest_id = None
            closest_distance = None
            for object_id, state in self.objects.items():
                distance = ((cent[0] - state["centroid"][0]) ** 2 + (cent[1] - state["centroid"][1]) ** 2) ** 0.5
                if closest_distance is None or distance < closest_distance:
                    closest_id = object_id
                    closest_distance = distance

            if closest_id is None or closest_distance is None or closest_distance > 200:
                object_id = self.next_object_id
                self.next_object_id += 1
                self.objects[object_id] = {"centroid": cent, "bbox": bbox}
                self.disappeared[object_id] = 0
                tracked.append({"id": object_id, "bbox": bbox, "centroid": cent})
                continue

            self.objects[closest_id] = {"centroid": cent, "bbox": bbox}
            self.disappeared[closest_id] = 0
            tracked.append({"id": closest_id, "bbox": bbox, "centroid": cent})

        for object_id in list(self.objects.keys()):
            if object_id not in {item["id"] for item in tracked}:
                self.disappeared[object_id] = self.disappeared.get(object_id, 0) + 1
                if self.disappeared[object_id] > self.max_disappeared:
                    del self.objects[object_id]
                    del self.disappeared[object_id]

        return tracked
