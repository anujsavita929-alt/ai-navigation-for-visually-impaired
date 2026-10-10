import queue
import threading
import unittest
from voice.text_to_speech import SpeechOutput


class FakeEngine:
    def __init__(self):
        self.stop_calls = 0
    def stop(self):
        self.stop_calls += 1


class TTSTests(unittest.TestCase):
    def test_urgent_message_interrupts_and_replaces_queued_message(self):
        output = SpeechOutput.__new__(SpeechOutput)
        output.enabled = True
        output.rate = 175
        output._queue = queue.Queue(maxsize=1)
        output._lock = threading.Lock()
        output._speaking = threading.Event()
        output._speaking.set()
        output._closed = threading.Event()
        output._engine = FakeEngine()
        output._thread = None
        output._queue.put_nowait(("stale warning", False))
        output.say("Stop and assess your surroundings", urgent=True)
        self.assertEqual(output._engine.stop_calls, 1)
        self.assertEqual(output._queue.get_nowait(), ("Stop and assess your surroundings", True))

    def test_normal_messages_coalesce_to_latest(self):
        output = SpeechOutput.__new__(SpeechOutput)
        output.enabled = True
        output._queue = queue.Queue(maxsize=1)
        output._speaking = threading.Event()
        output._closed = threading.Event()
        output._engine = None
        output._thread = None
        output.say("old update")
        output.say("new update")
        self.assertEqual(output._queue.get_nowait(), ("new update", False))
