# Local face-matching models

The optional **Find a person** image mode uses these OpenCV Zoo models locally:

- YuNet face detection: [OpenCV Zoo model](https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet), licensed under MIT (`LICENSE-YUNET.txt`).
- SFace face recognition: [OpenCV Zoo model](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface), licensed under Apache 2.0 (`LICENSE-SFACE.txt`).

The model files are included so the feature does not need to download models or send uploaded photos to a third party at runtime. Reference and group-image uploads are temporary; only the annotated group-image result is retained in `backend/outputs`.
