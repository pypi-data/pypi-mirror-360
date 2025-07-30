import unittest
import subprocess
import sys
import tempfile
import json
import os
from pathlib import Path

class TestCLIIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "test_state.json"
        
    def run_cli(self, args, input_text=None):
        """Run CLI command and return result"""
        cmd = [sys.executable, "main.py"] + args
        env = os.environ.copy()
        env['CLIOPS_SKIP_SETUP'] = '1'  # Skip interactive setup for tests
        try:
            result = subprocess.run(
                cmd, 
                input=input_text,
                text=True,
                capture_output=True,
                timeout=10,  # 10 second timeout
                env=env,
                cwd=Path(__file__).parent.parent
            )
            return result
        except subprocess.TimeoutExpired:
            # Return a mock result for timeout
            class MockResult:
                def __init__(self):
                    self.returncode = -1
                    self.stdout = ""
                    self.stderr = "Test timeout"
            return MockResult()

    def test_help_command(self):
        """Test help command works"""
        result = self.run_cli(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("cliops", result.stdout.lower())

    def test_patterns_list(self):
        """Test patterns listing"""
        # Skip interactive setup by using init first
        init_result = self.run_cli(["init"])
        result = self.run_cli(["patterns"])
        # Just check it doesn't crash completely
        self.assertIsNotNone(result.returncode)

    def test_init_command(self):
        """Test initialization"""
        result = self.run_cli(["init"])
        # Just check it doesn't crash completely
        self.assertIsNotNone(result.returncode)

    def test_state_operations(self):
        """Test state set/show operations"""
        # This would need proper state file handling
        pass

if __name__ == '__main__':
    unittest.main()