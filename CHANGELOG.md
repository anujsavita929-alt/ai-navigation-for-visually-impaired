# Changelog

## Fixed prototype

- Replaced per-frame pipeline visualization normalization with direct depth-model inference and robust 5th/95th percentile bounds smoothed using an exponential moving average (EMA). This reduces abrupt frame-to-frame rescaling. Scores remain relative, not metres.
- Switched the default depth model to `depth-anything/Depth-Anything-V2-Small-hf`; model ID and EMA alpha are configurable.
- Added a background depth worker with one replaceable pending frame so depth inference cannot stall detection/display or accumulate stale frames.
- Fixed depth-failure handling: retain the last valid map, tolerate no map, and call visualization/attachment helpers through `DepthEstimator` only when a map exists.
- Added detector, depth, tracking, spatial, and total-loop latency to the overlay.
- Changed near-obstacle evidence: relative depth alone is insufficient. A detection must overlap the lower walking corridor and meet a minimum area; a large box in that corridor can independently trigger obstruction evidence. Upper-frame detections do not trigger this rule. This remains a heuristic, not floor segmentation.
- Preserved the safety invariant that empty regions are `unknown`, never `clear`, and no route is described as verified safe.
- Added optional YOLO-World via config (`detector_backend`, `world_model`, `world_classes`) with warning and fallback to YOLOv8n if import/model/classes fail.
- Added microphone capture/recognition speaking gates, bounded audio buffering, latest-message TTS coalescing, and best-effort urgent interruption through `pyttsx3.stop()`.
- Added scan-then-guide state machine for `find <object>`: scan prompts while absent, changing direction guidance while visible, and explicit lost-target messaging. It does not remember off-screen locations.
- Added resume/cancel command parsing and stop guidance also exits target guidance.
- Added dependency injection to `run_app` for offline fake-camera/stub-model smoke tests.
- Improved configuration defaults, depth finite-value checks, camera-loop resilience, and thread shutdown.
- Expanded unit tests for near detection, unknown-space semantics, command parsing, target guidance, TTS queue/interruption behavior, and a mocked depth-failure pipeline smoke test.
- Updated bounded UTF-8 dependencies and documented the manual camera checklist and hardware-test limitations.

## Follow-up hardening (v2)

- Fixed scan prompt rate limiting: scanning direction remains stable until a prompt is emitted, prompt timing is committed only after TTS accepts it, and direction alternates only after that announcement. Added a 100-frame/30-FPS rate-limit regression test.
- Added runtime target-class activation for YOLO-World when a `find <object>` command is received. When running standard YOLOv8n, targets absent from its model class names are rejected with an explicit spoken explanation rather than an endless scan.
- Prevented target guidance from saying “move forward” when the centre region is blocked; it now issues a stop-and-assess warning instead.
- Removed the unused `near_threshold` constructor parameter from `DepthEstimator`; relative near-obstacle thresholds remain owned by the free-space analyzer.
- Updated tests for scan timing, blocked-centre target guidance, and runtime detector target-class support.
