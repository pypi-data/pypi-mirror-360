import unittest
from mystats import mean,median

class TestCore(unittest.TestCase):

    def test_mean(self):
        self.assertEqual(mean([1,2,3]),2)
    
    def test_median(self):
        self.assertEqual(median([1,3,2]),2)
    
if __name__ =='__main__':
    unittest.main()
