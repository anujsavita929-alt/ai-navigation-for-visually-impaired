"""Non-blocking TTS with stale-message coalescing and best-effort urgent interruption."""
import logging
import queue
import threading


class SpeechOutput:
    def __init__(self, enabled=True, rate=175):
        self.enabled = bool(enabled)
        self.rate = int(rate)
        self._queue = queue.Queue(maxsize=1)
        self._speaking = threading.Event()
        self._closed = threading.Event()
        self._engine = None
        self._thread = None
        if self.enabled:
            try:
                import pyttsx3
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", self.rate)
                self._thread = threading.Thread(target=self._worker, name="tts-worker", daemon=True)
                self._thread.start()
            except Exception as exc:
                logging.warning("TTS unavailable: %s", exc)
                self.enabled = False

    @property
    def is_speaking(self):
        return self._speaking.is_set()

    def say(self, text, urgent=False):
        if not self.enabled or not text or self._closed.is_set():
            return
        item = (str(text), bool(urgent))
        if urgent:
            # pyttsx3.stop() interrupts the current utterance on common drivers. It is
            # best-effort because some platform drivers do not support cross-thread stop.
            try:
                if self._engine is not None and self._speaking.is_set():
                    self._engine.stop()
            except Exception as exc:
                logging.debug("TTS interruption request failed: %s", exc)
            self._drain_queue()
            try:
                self._queue.put_nowait(item)
            except queue.Full:
                pass
            return
        self._drain_queue()
        try:
            self._queue.put_nowait(item)
        except queue.Full:
            pass

    def _drain_queue(self):
        while True:
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                return

    def _worker(self):
        while not self._closed.is_set():
            try:
                item = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            if item is None:
                self._queue.task_done()
                break
            text, _urgent = item
            try:
                self._speaking.set()
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as exc:
                logging.warning("TTS error: %s", exc)
            finally:
                self._speaking.clear()
                self._queue.task_done()

    def close(self):
        self._closed.set()
        try:
            if self._engine is not None:
                self._engine.stop()
        except Exception:
            pass
        self._drain_queue()
        if self._thread and self._thread.is_alive():
            try:
                self._queue.put_nowait(None)
            except queue.Full:
                pass
            self._thread.join(timeout=2.0)
