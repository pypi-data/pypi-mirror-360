import unittest
import tempfile
import shutil
from pathlib import Path
from core.cache import Cache

class TestCache(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        # Mock the cache directory
        self.original_cache_dir = None
        
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_cache_operations(self):
        """Test basic cache operations"""
        cache = Cache()
        
        # Test set and get
        cache.set("test_key", "test_value")
        result = cache.get("test_key")
        self.assertEqual(result, "test_value")
        
        # Test non-existent key
        result = cache.get("non_existent")
        self.assertIsNone(result)
        
        # Test clear
        cache.clear()
        result = cache.get("test_key")
        self.assertIsNone(result)

    def test_cache_complex_data(self):
        """Test caching complex data structures"""
        cache = Cache()
        
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "string": "test"
        }
        
        cache.set("complex", complex_data)
        result = cache.get("complex")
        self.assertEqual(result, complex_data)

if __name__ == '__main__':
    unittest.main()