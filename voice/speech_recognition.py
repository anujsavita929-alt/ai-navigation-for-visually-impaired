"""Optional offline Vosk microphone listener with TTS echo suppression."""
import json
import logging
import queue
import threading


class VoiceListener:
    def __init__(self, model_path, callback, should_ignore=None):
        self.model_path = model_path
        self.callback = callback
        self.should_ignore = should_ignore or (lambda: False)
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self._run, name="voice-listener", daemon=True)
        self.thread.start()

    def _run(self):
        try:
            import sounddevice as sd
            from vosk import Model, KaldiRecognizer
            model = Model(self.model_path)
            recognizer = KaldiRecognizer(model, 16000)
            audio_queue = queue.Queue(maxsize=8)

            def clear_audio_queue():
                while True:
                    try:
                        audio_queue.get_nowait()
                    except queue.Empty:
                        return

            def audio_callback(indata, frames, time_info, status):
                if status:
                    logging.debug("Audio status: %s", status)
                if self.should_ignore():
                    clear_audio_queue()
                    return
                try:
                    audio_queue.put_nowait(bytes(indata))
                except queue.Full:
                    try:
                        audio_queue.get_nowait()
                    except queue.Empty:
                        pass
                    try:
                        audio_queue.put_nowait(bytes(indata))
                    except queue.Full:
                        pass

            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1,
                                   callback=audio_callback):
                logging.info("Offline voice listener started")
                while not self.stop_event.is_set():
                    try:
                        data = audio_queue.get(timeout=0.2)
                    except queue.Empty:
                        continue
                    if self.should_ignore():
                        clear_audio_queue()
                        try:
                            recognizer.Reset()
                        except Exception:
                            pass
                        continue
                    if recognizer.AcceptWaveform(data):
                        text = json.loads(recognizer.Result()).get("text", "").strip()
                        if text and not self.should_ignore():
                            self.callback(text)
        except Exception as exc:
            logging.warning("Voice listener unavailable: %s", exc)

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
