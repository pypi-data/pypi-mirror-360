import unittest
from unittest.mock import Mock
from core.optimizer import PromptOptimizer
from core.patterns import OptimizationPattern

class TestPromptOptimizer(unittest.TestCase):
    def setUp(self):
        self.mock_cli_state = Mock()
        self.mock_cli_state.state = {"ARCHITECTURE": "Test Architecture"}
        self.mock_cli_state.get.return_value = "Test Architecture"
        
        self.mock_pattern_registry = Mock()
        self.test_pattern = OptimizationPattern(
            name="test_pattern",
            description="Test pattern",
            template="# DIRECTIVE: {directive}\n## CONTEXT: {context}\n{code_here}",
            principles=["Test"]
        )
        self.mock_pattern_registry.get_pattern.return_value = self.test_pattern
        
        self.optimizer = PromptOptimizer(self.mock_pattern_registry, self.mock_cli_state)

    def test_parse_prompt_into_sections(self):
        prompt = "## DIRECTIVE:\nTest directive\n## CONTEXT:\nTest context\n<CODE>test code</CODE>"
        sections = self.optimizer._parse_prompt_into_sections(prompt)
        
        self.assertIn("DIRECTIVE", sections)
        self.assertIn("CONTEXT", sections)
        self.assertIn("CODE_HERE", sections)
        self.assertEqual(sections["DIRECTIVE"], "Test directive")
        self.assertEqual(sections["CONTEXT"], "Test context")
        self.assertEqual(sections["CODE_HERE"], "test code")

    def test_optimize_prompt_basic(self):
        raw_prompt = "## DIRECTIVE:\nCreate a function\n## CONTEXT:\nPython project"
        result = self.optimizer.optimize_prompt(raw_prompt, "test_pattern", {})
        
        self.assertIn("Create a function", result)
        self.assertIn("Python project", result)

    def test_optimize_prompt_with_overrides(self):
        raw_prompt = "## DIRECTIVE:\nCreate a function"
        overrides = {"context": "Override context"}
        result = self.optimizer.optimize_prompt(raw_prompt, "test_pattern", overrides)
        
        # Check that directive is preserved
        self.assertIn("Create a function", result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()