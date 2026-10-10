# Model files

- YOLO weights: the default `yolov8n.pt` is downloaded by Ultralytics on first use if it is not already available. Download requires network access unless you supply the file yourself.
- Depth model: the configured Hugging Face model is downloaded by Transformers on first use. First-time download requires network access and enough disk space.
- Offline speech: download a Vosk English model separately and extract it under `models/` so that `config/settings.yaml` points to the extracted directory. See https://alphacephei.com/vosk/models. Speech recognition will be unavailable until this optional model and dependencies are installed.

Model licenses and distribution terms vary. This ZIP intentionally does not bundle large model weights.
