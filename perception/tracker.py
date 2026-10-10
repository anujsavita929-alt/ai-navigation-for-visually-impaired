"""Simple IoU-based association for visible detections; not a safety-grade tracker."""


class SimpleTracker:
    def __init__(self, iou_threshold=0.25, max_missed=5):
        self.iou_threshold = float(iou_threshold)
        self.max_missed = int(max_missed)
        self.tracks = {}
        self.next_id = 1

    @staticmethod
    def iou(box_a, box_b):
        x1 = max(box_a[0], box_b[0])
        y1 = max(box_a[1], box_b[1])
        x2 = min(box_a[2], box_b[2])
        y2 = min(box_a[3], box_b[3])
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area_a = max(0, box_a[2] - box_a[0]) * max(0, box_a[3] - box_a[1])
        area_b = max(0, box_b[2] - box_b[0]) * max(0, box_b[3] - box_b[1])
        union = area_a + area_b - intersection
        return intersection / max(union, 1e-9)

    def update(self, detections):
        for track in self.tracks.values():
            track["missed"] += 1

        used_track_ids = set()
        for detection in detections:
            best_id = None
            best_iou = 0.0
            for track_id, track in self.tracks.items():
                if track_id in used_track_ids or track["label"] != detection.label:
                    continue
                overlap = self.iou(detection.xyxy, track["box"])
                if overlap > best_iou:
                    best_iou = overlap
                    best_id = track_id

            if best_id is not None and best_iou >= self.iou_threshold:
                detection.track_id = best_id
                self.tracks[best_id] = {
                    "box": detection.xyxy,
                    "label": detection.label,
                    "missed": 0,
                }
                used_track_ids.add(best_id)
            else:
                track_id = self.next_id
                self.next_id += 1
                detection.track_id = track_id
                self.tracks[track_id] = {
                    "box": detection.xyxy,
                    "label": detection.label,
                    "missed": 0,
                }
                used_track_ids.add(track_id)

        self.tracks = {
            track_id: track
            for track_id, track in self.tracks.items()
            if track["missed"] <= self.max_missed
        }
        return detections
