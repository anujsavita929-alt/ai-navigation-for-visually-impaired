import unittest
from perception.detector import YOLODetector


class FakeWorldModel:
    def __init__(self):
        self.names = {0: "chair", 1: "person"}
        self.set_calls = []
    def set_classes(self, classes):
        self.set_calls.append(list(classes))


class DetectorTargetTests(unittest.TestCase):
    def test_world_backend_adds_unknown_requested_target(self):
        detector = YOLODetector.__new__(YOLODetector)
        detector.backend = "yolo-world"
        detector.model = FakeWorldModel()
        detector.world_classes = ["chair", "person"]
        self.assertTrue(detector.ensure_target_class("fire extinguisher"))
        self.assertEqual(detector.model.set_calls[-1], ["chair", "person", "fire extinguisher"])

    def test_coco_backend_rejects_non_coco_target(self):
        detector = YOLODetector.__new__(YOLODetector)
        detector.backend = "yolo"
        detector.model = FakeWorldModel()
        self.assertTrue(detector.ensure_target_class("chair"))
        self.assertFalse(detector.ensure_target_class("fire extinguisher"))
