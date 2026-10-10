import unittest
from voice.command_parser import CommandParser


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.parser = CommandParser()

    def test_find_my_target(self):
        result = self.parser.parse("find my bottle")
        self.assertEqual(result, {"intent": "find", "target": "bottle"})

    def test_scene(self):
        self.assertEqual(self.parser.parse("what is in front of me")["intent"], "scene")

    def test_stop_and_resume(self):
        self.assertEqual(self.parser.parse("stop guidance")["intent"], "stop")
        self.assertEqual(self.parser.parse("resume guidance")["intent"], "resume")

    def test_empty_and_unknown(self):
        self.assertEqual(self.parser.parse("   ")["intent"], "unknown")
        self.assertEqual(self.parser.parse("hello there")["intent"], "unknown")


if __name__ == "__main__":
    unittest.main()
