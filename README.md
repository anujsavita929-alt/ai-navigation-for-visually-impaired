# Depth-Aware AI Navigation Assistant — Fixed Prototype

A modular Python prototype combining camera capture, YOLO object detection, optional monocular relative depth, lightweight tracking, conservative left/centre/right image-region heuristics, and optional offline voice interaction.

> **Safety notice:** This is an experimental prototype, not a certified mobility aid. Do not use it as the sole means of navigation. It does not replace a white cane, guide dog, or mobility training. The image-region heuristic does not prove that a route is traversable or safe.

## Included

- OpenCV webcam/IP camera input with reconnection attempts.
- YOLOv8n default detector; optional YOLO-World open-vocabulary detector.
- Configurable monocular depth model running asynchronously with temporally smoothed relative scores.
- Simple IoU tracking, scene representation, and conservative obstruction heuristics.
- Scan-then-guide target search, optional Vosk speech recognition, and pyttsx3 TTS.
- Offline unit tests and fake-camera pipeline smoke test.

## Installation

Python 3.10–3.12 recommended. Model weights are downloaded on first use and are not included in this ZIP.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

PyTorch installation depends on OS and CUDA version. For GPU use, install the matching build from https://pytorch.org/get-started/locally/ . `device: auto` does not guarantee GPU support.

## Run

```bash
python main.py
python main.py --source 0 --no-depth
python main.py --source "http://PHONE_IP:PORT/video"
python main.py --no-voice
```

The `--source`, `--no-depth`, and `--no-voice` flags are supported. Press `q` to quit, `s` to speak the current assessment, and `i` to speak visible detection labels. Keyboard shortcuts require the OpenCV window to be focused.

## Configuration

Edit `config/settings.yaml`:

- `camera.source`: `"0"` for the default webcam, `"1"` for another camera, or an IP stream URL.
- `perception.detector_backend`: `yolo` (default) or `yolo-world`. YOLO-World needs a non-empty `world_classes` list; failures fall back to YOLOv8n.
- `perception.depth_model`: Hugging Face depth-estimation model ID.
- `perception.depth_bounds_ema_alpha`: lower values smooth scene normalization more strongly.
- `navigation.near_relative_depth_threshold`, `corridor_y_start`, and box-area thresholds tune the heuristic; they are not calibrated distance thresholds.

## Depth and safety interpretation

Depth scores are **relative only**, not metres. EMA-smoothed robust normalization reduces abrupt rescaling but cannot make monocular depth physically calibrated or comparable across arbitrary scenes. Model polarity and output quality should be checked visually. Empty image regions remain `unknown`, not `clear`. No path is verified safe. Transparent objects, drop-offs, overhangs, low obstacles, occlusions, and objects outside the camera view may be missed.

## Voice commands

Examples: “What is in front of me?”, “How far is the nearest object?”, “Find my bottle”, “Stop guidance”, “Resume guidance”, “Repeat”. Find mode scans the current camera view, provides direction guidance while the target is detected, and reports when it is lost. It does not remember the location of an object after it leaves the frame. Download a Vosk model and set `voice.vosk_model_path`; microphone and TTS behavior depends on platform audio drivers. Urgent TTS interruption is best-effort.

## Tests

From the project root:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

The pipeline smoke test uses a fake camera and stubs; it does not require camera hardware or downloaded model weights.

## Manual camera test checklist

1. **Camera only:** run `python -m camera_input.camera_test --source 0` (or use your phone stream URL). Confirm the video is stable and correctly oriented; verify reconnect behavior by briefly disconnecting the stream.
2. **Detection baseline:** run `python main.py --no-depth --no-voice`. Move a chair or person across the view. Labels/boxes should update without depth-model stalls; confirm `q` exits.
3. **Depth overlay:** enable depth and inspect the relative-depth window on an empty hallway, then with a nearby object. Scores should not be interpreted as metres; the detection/display loop should continue while depth inference runs.
4. **Corridor heuristic:** in a controlled setting, place a small object low in the centre, then high in the frame. The lower-corridor object should provide stronger obstruction evidence; the upper object should not trigger the near-corridor rule solely because of its relative score. Empty regions should remain `unknown`.
5. **Latency and load:** watch detector/depth/tracking/spatial/loop timings and FPS for several minutes. Note hardware, model, and resolution if latency spikes or the display drops frames.
6. **Target guide:** say “Find my chair” or use a supported command. When absent, expect slow scan prompts; when visible, expect changing left/centre/right guidance; after occlusion or leaving view, expect an explicit lost-target message rather than a claimed remembered location.
7. **Voice echo and interruption:** with microphone and speakers enabled, verify the system does not treat its own speech as a command. Trigger an urgent warning during a longer utterance; the old utterance should stop when the platform driver supports interruption, and stale queued updates should not play later.
8. **Fail-safe behavior:** test with depth disabled, then with a deliberately unavailable depth model. Detection should continue, empty regions must not be called clear, and no message should claim a path is verified safe.

Perform manual tests in a controlled area with a spotter. Do not test by walking into obstacles or rely on this prototype as a mobility aid.

## What has not been verified

This package was checked with compile and unit/smoke tests only. A real camera/phone stream, GPU/CUDA acceleration, model download and inference quality, microphone permissions, and platform-specific pyttsx3 interruption were not tested in this environment. Performance and navigation accuracy remain hardware- and scene-dependent.
