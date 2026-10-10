"""Resilient OpenCV webcam/IP-stream reader."""
import logging
import time

import cv2


class CameraStream:
    def __init__(self, source=0, width=640, height=480, reconnect_attempts=3,
                 reconnect_delay_seconds=1.0):
        self.source = source
        self.width = width
        self.height = height
        self.reconnect_attempts = max(0, int(reconnect_attempts))
        self.reconnect_delay = max(0.0, float(reconnect_delay_seconds))
        self.cap = None

    @staticmethod
    def parse_source(source):
        if isinstance(source, int):
            return source
        value = str(source).strip()
        return int(value) if value.isdigit() else value

    def open(self):
        self.release()
        self.cap = cv2.VideoCapture(self.parse_source(self.source))
        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if not self.cap.isOpened():
            self.release()
            raise RuntimeError(
                f"Unable to open camera source: {self.source!r}. Check URL, network, and camera server."
            )
        logging.info("Camera opened: %s", self.source)
        return self

    def read(self):
        if self.cap is None or not self.cap.isOpened():
            for attempt in range(self.reconnect_attempts):
                logging.warning(
                    "Camera disconnected; reconnect attempt %d/%d",
                    attempt + 1, self.reconnect_attempts,
                )
                time.sleep(self.reconnect_delay)
                try:
                    self.open()
                    break
                except RuntimeError:
                    continue
            else:
                return False, None

        ok, frame = self.cap.read()
        if not ok or frame is None:
            logging.warning("Failed to read camera frame")
            self.release()
            return False, None
        return True, frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __enter__(self):
        return self.open()

    def __exit__(self, *_):
        self.release()
