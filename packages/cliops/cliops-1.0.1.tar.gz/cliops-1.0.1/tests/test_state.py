import unittest
import tempfile
import json
from pathlib import Path
from core.state import CLIState

class TestCLIState(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.state_file = Path(self.temp_file.name)
        self.cli_state = CLIState(self.state_file)

    def tearDown(self):
        if self.state_file.exists():
            self.state_file.unlink()

    def test_set_and_get(self):
        self.cli_state.set("TEST_KEY", "test_value")
        self.assertEqual(self.cli_state.get("TEST_KEY"), "test_value")
        self.assertEqual(self.cli_state.get("test_key"), "test_value")  # Case insensitive

    def test_persistence(self):
        self.cli_state.set("PERSIST_KEY", "persist_value")
        
        # Create new instance to test persistence
        new_cli_state = CLIState(self.state_file)
        self.assertEqual(new_cli_state.get("PERSIST_KEY"), "persist_value")

    def test_clear(self):
        self.cli_state.set("CLEAR_KEY", "clear_value")
        self.cli_state.clear()
        self.assertIsNone(self.cli_state.get("CLEAR_KEY"))

    def test_nonexistent_key(self):
        self.assertIsNone(self.cli_state.get("NONEXISTENT"))

if __name__ == '__main__':
    unittest.main()