"""Monocular depth estimation with temporally stable relative-depth scores.

Scores are relative scene cues, never calibrated physical distances.
"""
from __future__ import annotations

import logging
import time
import numpy as np


class DepthEstimator:
    def __init__(self, model_id="depth-anything/Depth-Anything-V2-Small-hf", device="auto",
                 ema_alpha=0.12):
        try:
            import torch
            from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        except ImportError as exc:
            raise RuntimeError("Depth dependencies missing. Install requirements.txt and enable depth.") from exc

        self.torch = torch
        if str(device).startswith("cuda"):
            self.device = str(device)
        elif device == "auto" and torch.cuda.is_available():
            self.device = "cuda:0"
        else:
            self.device = "cpu"
        self.processor = AutoImageProcessor.from_pretrained(model_id)
        self.model = AutoModelForDepthEstimation.from_pretrained(model_id).to(self.device).eval()
        self.model_id = model_id
        self.ema_alpha = float(np.clip(ema_alpha, 0.01, 1.0))
        self._bounds = None
        self.last_map = None
        logging.info("Loaded depth model %s on %s", model_id, self.device)

    def estimate(self, frame):
        import cv2
        from PIL import Image

        started = time.perf_counter()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        inputs = self.processor(images=Image.fromarray(rgb), return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with self.torch.inference_mode():
            output = self.model(**inputs).predicted_depth
            raw = self.torch.nn.functional.interpolate(
                output.unsqueeze(1), size=frame.shape[:2], mode="bicubic", align_corners=False
            ).squeeze().detach().float().cpu().numpy()

        finite = raw[np.isfinite(raw)]
        if finite.size < 16:
            raise RuntimeError("Depth model returned an invalid depth map")
        # Depth Anything/MiDaS-style inverse-depth outputs generally increase toward nearer surfaces.
        # EMA-smoothed robust bounds prevent sudden frame-to-frame rescaling; this remains relative.
        lo, hi = np.percentile(finite, [5, 95]).astype(float)
        if hi - lo < 1e-6:
            hi = lo + 1e-6
        if self._bounds is None:
            self._bounds = (lo, hi)
        else:
            alpha = self.ema_alpha
            old_lo, old_hi = self._bounds
            self._bounds = (alpha * lo + (1 - alpha) * old_lo,
                            alpha * hi + (1 - alpha) * old_hi)
        stable_lo, stable_hi = self._bounds
        normalized = np.clip((raw - stable_lo) / max(stable_hi - stable_lo, 1e-6), 0.0, 1.0)
        normalized[~np.isfinite(normalized)] = 0.0
        self.last_map = normalized.astype(np.float32)
        return self.last_map, time.perf_counter() - started

    @staticmethod
    def colorize(depth_map):
        import cv2
        gray = np.uint8(np.clip(depth_map, 0, 1) * 255)
        return cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)

    @staticmethod
    def attach_depth(detections, depth_map):
        """Attach a robust median score for each bounding box; score is relative, not metres."""
        if depth_map is None or getattr(depth_map, "size", 0) == 0:
            return detections
        h, w = depth_map.shape[:2]
        for detection in detections:
            x1, y1, x2, y2 = map(int, detection.xyxy)
            x1, x2 = max(0, min(w, x1)), max(0, min(w, x2))
            y1, y2 = max(0, min(h, y1)), max(0, min(h, y2))
            if x2 > x1 and y2 > y1:
                region = depth_map[y1:y2, x1:x2]
                values = region[np.isfinite(region)]
                if values.size:
                    detection.relative_depth = float(np.median(values))
        return detections
