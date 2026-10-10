import unittest
from navigation.navigation_engine import NavigationEngine
from spatial.free_space import FreeSpaceAnalyzer
from perception.detector import Detection
class NavigationTests(unittest.TestCase):
 def test_unknown_does_not_claim_safe(self):
  d=NavigationEngine().decide({'regions':{'left':'unknown','centre':'unknown','right':'unknown'}})
  self.assertIsNone(d['direction']); self.assertIn('cannot verify',d['text'].lower())
 def test_blocked_centre_warns(self):
  d=NavigationEngine().decide({'regions':{'left':'caution','centre':'blocked','right':'unknown'}})
  self.assertIn('Obstacle detected ahead',d['text'])
 def test_free_space_absence_is_unknown(self):
  a=FreeSpaceAnalyzer(); r=a.analyze([], (480,640,3)); self.assertEqual(r['regions']['centre'],'unknown')
if __name__=='__main__': unittest.main()
