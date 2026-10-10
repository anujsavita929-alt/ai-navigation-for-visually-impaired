import unittest
from perception.detector import Detection
from spatial.free_space import FreeSpaceAnalyzer


class FreeSpaceTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = FreeSpaceAnalyzer(near_threshold=0.72, large_box_area=0.12, corridor_area=0.025,
                                          corridor_y_start=0.48)
        self.shape = (480, 640, 3)

    def test_near_relative_score_requires_lower_corridor_and_nontrivial_box(self):
        tiny_box = Detection("chair", 0.9, (280, 350, 310, 380), relative_depth=0.99)
        result = self.analyzer.analyze([tiny_box], self.shape)
        self.assertEqual(result["regions"]["centre"], "caution")

    def test_near_detection_in_lower_centre_corridor_is_blocked(self):
        box = Detection("chair", 0.9, (250, 300, 390, 440), relative_depth=0.91)
        result = self.analyzer.analyze([box], self.shape)
        self.assertEqual(result["regions"]["centre"], "blocked")
        self.assertTrue(result["evidence"]["centre"][0]["in_walking_corridor"])

    def test_large_upper_frame_object_does_not_trigger_near_corridor_rule(self):
        box = Detection("picture", 0.95, (220, 20, 430, 180), relative_depth=0.99)
        result = self.analyzer.analyze([box], self.shape)
        self.assertEqual(result["regions"]["centre"], "caution")

    def test_empty_regions_remain_unknown(self):
        result = self.analyzer.analyze([], self.shape)
        self.assertEqual(result["regions"], {"left": "unknown", "centre": "unknown", "right": "unknown"})
