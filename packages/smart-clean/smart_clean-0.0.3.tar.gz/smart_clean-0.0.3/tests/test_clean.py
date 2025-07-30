import unittest
import time
from control import clean_, CleanStrategy, CleaningError

class TestCleaning(unittest.TestCase):
    def test_basic_cleaning(self):
        result = clean_(duration=0.1)
        self.assertTrue(result)

    def test_aggressive_cleaning(self):
        result = clean_(duration=0.1, strategy=CleanStrategy.AGGRESSIVE)
        self.assertTrue(result)

    def test_force_cleaning(self):
        result = clean_(duration=0.1, force=True)
        self.assertTrue(result)

    def test_invalid_duration(self):
        with self.assertRaises(ValueError):
            clean_(duration=-1)

if __name__ == '__main__':
    unittest.main() 