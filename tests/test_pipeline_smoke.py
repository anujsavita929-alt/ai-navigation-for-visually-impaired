import unittest
import time
import numpy as np
from app.pipeline import run_app
from perception.detector import Detection


class FakeCamera:
    def __init__(self, *args):
        self.frames = 0
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def read(self):
        self.frames += 1
        if self.frames > 2:
            return False, None
        return True, np.zeros((120, 160, 3), dtype=np.uint8)


class FakeDetector:
    def predict(self, frame):
        time.sleep(0.03)
        return [Detection("chair", .9, (50, 45, 100, 115), relative_depth=None)], 0.001
    @staticmethod
    def annotate(frame, detections):
        return frame


class BrokenDepth:
    def __init__(self):
        self.calls = 0
    def estimate(self, frame):
        self.calls += 1
        raise RuntimeError("deliberate mocked depth failure")


class FakeSpeech:
    is_speaking = False
    def __init__(self):
        self.messages = []
    def say(self, text, urgent=False):
        self.messages.append((text, urgent))
    def close(self):
        pass


class PipelineSmokeTests(unittest.TestCase):
    def test_depth_failure_does_not_crash_pipeline(self):
        config = {
            "camera": {"source": "fake", "width": 160, "height": 120,
                       "reconnect_attempts": 0, "reconnect_delay_seconds": 0},
            "perception": {"enable_depth": True, "depth_every_n_frames": 1, "enable_tracking": True},
            "navigation": {"near_relative_depth_threshold": .72, "speech_cooldown_seconds": 3},
            "voice": {"enabled": False, "tts_enabled": False},
            "app": {"show_depth_window": False, "log_level": "CRITICAL"},
        }
        broken_depth = BrokenDepth()
        run_app(config, camera_factory=FakeCamera, detector=FakeDetector(),
                depth_estimator=broken_depth, speech=FakeSpeech(), max_frames=2, display=False)
        self.assertGreaterEqual(broken_depth.calls, 1)
