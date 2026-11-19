import unittest,json
from pathlib import Path
class TestData(unittest.TestCase):
 def test_seed(self):
  r=json.loads((Path(__file__).resolve().parents[1]/'data/resources.json').read_text())['resources'];self.assertGreaterEqual(len(r),25);self.assertEqual(len({x['url'] for x in r}),len(r));self.assertTrue(all(x['url'].startswith('https://') and x['topics'] for x in r))
