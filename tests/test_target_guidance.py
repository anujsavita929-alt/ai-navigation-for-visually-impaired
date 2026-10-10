import unittest
from navigation.target_guidance import TargetGuidance
from spatial.world_model import SceneObject


class TargetGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.guidance = TargetGuidance(announce_interval=1.0)
        self.guidance.start("chair")

    def test_scans_when_target_not_visible(self):
        message = self.guidance.update({"objects": []}, now=10.0)
        self.assertIn("turn slowly left", message.lower())
        self.assertEqual(self.guidance.state, "scanning")

    def test_guides_visible_target_and_reports_loss(self):
        target = SceneObject("chair", .9, (450, 200, 520, 350), .76, .55, "right", .8, 12)
        message = self.guidance.update({"objects": [target]}, now=11.0)
        self.assertIn("slightly right", message.lower())
        self.assertEqual(self.guidance.state, "guiding")
        lost = self.guidance.update({"objects": []}, now=12.0)
        self.assertIn("lost sight", lost.lower())
        self.assertIn("do not know where it went", lost.lower())
        self.assertEqual(self.guidance.state, "lost")

    def test_prefers_current_visible_tracker_id(self):
        tracked = SceneObject("chair", .7, (250, 200, 350, 350), .47, .55, "centre", .8, 12)
        distractor = SceneObject("chair", .99, (450, 200, 550, 350), .78, .55, "right", .9, 99)
        self.guidance.update({"objects": [tracked]}, now=10.0)
        message = self.guidance.update({"objects": [distractor, tracked]}, now=12.0)
        self.assertIn("found ahead", message.lower())
        self.assertEqual(self.guidance.active_track_id, 12)

    def test_repeated_same_guidance_is_rate_limited(self):
        target = SceneObject("chair", .9, (250, 200, 350, 350), .47, .55, "centre", .8, 12)
        self.assertIsNotNone(self.guidance.update({"objects": [target]}, now=10.0))
        self.assertIsNone(self.guidance.update({"objects": [target]}, now=10.5))

    def test_scan_announcements_obey_interval_over_100_frames(self):
        guidance = TargetGuidance(announce_interval=2.0)
        guidance.start("chair")
        announcements = []
        for frame in range(100):
            now = frame / 30.0
            message = guidance.update({"objects": []}, now=now)
            if message:
                announcements.append((now, message))
                guidance.mark_spoken(now)
        self.assertLessEqual(len(announcements), 3)
        self.assertTrue(all(
            later[0] - earlier[0] >= 2.0
            for earlier, later in zip(announcements, announcements[1:])
        ))
        self.assertIn("left", announcements[0][1].lower())
        if len(announcements) > 1:
            self.assertIn("right", announcements[1][1].lower())

    def test_blocked_centre_never_guides_forward(self):
        guidance = TargetGuidance(announce_interval=1.0)
        guidance.start("chair")
        target = SceneObject("chair", .9, (450, 200, 520, 350), .75, .55, "right", .8, 12)
        message = guidance.update({"objects": [target]}, now=10.0, centre_blocked=True)
        self.assertIn("centre region is blocked", message.lower())
        self.assertIn("do not move forward", message.lower())
        self.assertNotIn("move forward slowly", message.lower())
