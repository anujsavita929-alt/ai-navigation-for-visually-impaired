"""Single-slot background worker: latest frame wins, so inference never queues up."""
from __future__ import annotations
import logging
import threading
import time


class DepthWorker:
    def __init__(self, estimator):
        self.estimator = estimator
        self._condition = threading.Condition()
        self._pending = None
        self._closed = False
        self._latest_map = None
        self._latest_duration = 0.0
        self._latest_completed_at = 0.0
        self._latest_error = None
        self._result_id = 0
        self._thread = threading.Thread(target=self._run, name="depth-inference", daemon=True)
        self._thread.start()

    def submit(self, frame, frame_id):
        with self._condition:
            if self._closed:
                return
            self._pending = (frame.copy(), frame_id)
            self._condition.notify()

    def snapshot(self):
        with self._condition:
            return (
                self._latest_map,
                self._latest_duration,
                self._result_id,
                self._latest_error,
                self._latest_completed_at,
            )

    def _run(self):
        while True:
            with self._condition:
                while self._pending is None and not self._closed:
                    self._condition.wait()
                if self._closed:
                    return
                frame, frame_id = self._pending
                self._pending = None
            try:
                depth_map, duration = self.estimator.estimate(frame)
                with self._condition:
                    self._latest_map = depth_map.copy()
                    self._latest_duration = duration
                    self._result_id = frame_id
                    self._latest_completed_at = time.perf_counter()
                    self._latest_error = None
            except Exception as exc:
                logging.warning("Background depth inference failed: %s", exc)
                with self._condition:
                    self._latest_error = str(exc)

    def close(self, timeout=2.0):
        with self._condition:
            self._closed = True
            self._condition.notify_all()
        self._thread.join(timeout=timeout)
