import unittest
import subprocess
import tempfile
import os
from pathlib import Path

class TestCLIIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir

    def tearDown(self):
        if self.original_home:
            os.environ['HOME'] = self.original_home
        else:
            os.environ.pop('HOME', None)

    def run_cliops(self, args):
        """Helper to run cliops command and return result"""
        cmd = ['python', 'main.py'] + args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        return result

    def test_init_command(self):
        result = self.run_cliops(['init'])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Initialization complete", result.stdout)

    def test_state_set_and_show(self):
        # Set state
        result = self.run_cliops(['state', 'set', 'TEST_KEY', 'test_value'])
        self.assertEqual(result.returncode, 0)
        
        # Show state
        result = self.run_cliops(['state', 'show'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('TEST_KEY', result.stdout)

    def test_patterns_list(self):
        result = self.run_cliops(['patterns'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('context_aware_generati', result.stdout)  # Truncated in table display

    def test_optimize_basic(self):
        result = self.run_cliops(['optimize', 'Create a function', '--dry-run'])
        self.assertEqual(result.returncode, 0)
        self.assertIn('Dry run complete', result.stdout)

if __name__ == '__main__':
    unittest.main()