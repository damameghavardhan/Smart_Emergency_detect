import base64
import time

import cv2
from PyQt6.QtCore import QThread, pyqtSignal


class CameraWorker(QThread):
    """Read webcam frames off the UI thread and forward them as Qt images."""

    frame_ready = pyqtSignal(str)
    camera_error = pyqtSignal(str)

    def __init__(self, camera_index: int = 0, preview_fps: int = 15) -> None:
        super().__init__()
        self.camera_index = camera_index
        self.preview_fps = max(1, min(preview_fps, 30))

    def run(self) -> None:
        capture = cv2.VideoCapture(self.camera_index)
        if not capture.isOpened():
            capture.release()
            self.camera_error.emit(
                f"Camera {self.camera_index} could not be opened. Check its connection or index."
            )
            return

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        frame_interval = 1 / self.preview_fps
        next_frame_at = 0.0

        try:
            while not self.isInterruptionRequested():
                delay = next_frame_at - time.monotonic()
                if delay > 0:
                    time.sleep(delay)

                success, frame = capture.read()
                if not success:
                    self.camera_error.emit("The camera stopped returning frames.")
                    break

                height, width = frame.shape[:2]
                scale = min(1.0, 640 / width, 360 / height)
                if scale < 1.0:
                    frame = cv2.resize(
                        frame,
                        (int(width * scale), int(height * scale)),
                        interpolation=cv2.INTER_AREA,
                    )

                encoded, jpeg = cv2.imencode(
                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 72]
                )
                if encoded:
                    self.frame_ready.emit(base64.b64encode(jpeg).decode("ascii"))
                next_frame_at = time.monotonic() + frame_interval
        finally:
            capture.release()