"""State machine for explicitly requested scan-then-guide target finding."""


class TargetGuidance:
    def __init__(self, announce_interval=2.0):
        self.announce_interval = float(announce_interval)
        self.target = None
        self.state = "idle"
        self.scan_direction = "left"
        self.last_announcement = 0.0
        self.last_message = ""
        self.active_track_id = None
        self._pending_scan_direction = None

    def start(self, target):
        self.target = str(target).strip().lower()
        self.state = "scanning"
        self.scan_direction = "left"
        self.last_announcement = 0.0
        self.last_message = ""
        self.active_track_id = None
        self._pending_scan_direction = None

    def stop(self):
        self.target = None
        self.state = "idle"
        self.last_message = ""
        self.active_track_id = None
        self._pending_scan_direction = None

    def mark_spoken(self, now):
        """Commit announcement timing and scan alternation after TTS accepts a prompt."""
        if self._pending_scan_direction is not None:
            self.scan_direction = "right" if self._pending_scan_direction == "left" else "left"
            self._pending_scan_direction = None

    def update(self, scene, now, centre_blocked=False):
        if self.state == "idle" or not self.target:
            return None

        visible_targets = [
            obj for obj in scene.get("objects", [])
            if self.target in obj.label.lower()
        ]
        if visible_targets:
            # Prefer the same tracker ID while it remains visible; otherwise select a
            # current-frame match. No position is retained after the target disappears.
            target = next(
                (obj for obj in visible_targets if obj.track_id == self.active_track_id),
                None,
            )
            if target is None:
                target = max(
                    visible_targets,
                    key=lambda obj: (
                        obj.confidence,
                        max(0, obj.bbox[2] - obj.bbox[0]) * max(0, obj.bbox[3] - obj.bbox[1]),
                    ),
                )
            self.active_track_id = target.track_id
            self.state = "guiding"
            if centre_blocked:
                message = (
                    f"{self.target} is visible, but the centre region is blocked. Stop and assess; "
                    "do not move forward."
                )
            elif target.center_x < 0.38:
                message = f"{self.target} found. Slightly left; turn toward it and move forward slowly."
            elif target.center_x > 0.62:
                message = f"{self.target} found. Slightly right; turn toward it and move forward slowly."
            else:
                message = f"{self.target} found ahead. Keep it in view and move forward slowly."
        else:
            self.active_track_id = None
            if self.state == "guiding":
                self.state = "lost"
                message = (
                    f"I lost sight of the {self.target}. Stop and scan slowly; "
                    "I do not know where it went."
                )
            else:
                self.state = "scanning"
                if now - self.last_announcement < self.announce_interval:
                    return None
                message = (
                    f"I cannot see the {self.target}. Turn slowly {self.scan_direction} "
                    "to scan the current view."
                )
                self._pending_scan_direction = self.scan_direction

        if now - self.last_announcement >= self.announce_interval:
            self.last_message = message
            self.last_announcement = float(now)
            return message
        return None
