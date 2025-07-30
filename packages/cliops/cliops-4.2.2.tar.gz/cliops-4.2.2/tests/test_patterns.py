import unittest
from unittest.mock import Mock
from core.patterns import OptimizationPattern, PatternRegistry

class TestOptimizationPattern(unittest.TestCase):
    def test_from_dict(self):
        data = {
            "name": "test_pattern",
            "description": "Test pattern",
            "template": "Test template: {field}",
            "principles": ["Test Principle"]
        }
        pattern = OptimizationPattern.from_dict(data)
        self.assertEqual(pattern.name, "test_pattern")
        self.assertEqual(pattern.description, "Test pattern")
        self.assertEqual(pattern.template, "Test template: {field}")
        self.assertEqual(pattern.principles, ["Test Principle"])

    def test_to_dict(self):
        pattern = OptimizationPattern(
            name="test_pattern",
            description="Test pattern",
            template="Test template: {field}",
            principles=["Test Principle"]
        )
        result = pattern.to_dict()
        expected = {
            "name": "test_pattern",
            "description": "Test pattern",
            "template": "Test template: {field}",
            "principles": ["Test Principle"]
        }
        self.assertEqual(result, expected)

class TestPatternRegistry(unittest.TestCase):
    def setUp(self):
        self.mock_cli_state = Mock()
        self.mock_cli_state.state = {}
        self.registry = PatternRegistry(self.mock_cli_state)

    def test_get_pattern(self):
        pattern = self.registry.get_pattern("context_aware_generation")
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.name, "context_aware_generation")

    def test_get_nonexistent_pattern(self):
        pattern = self.registry.get_pattern("nonexistent_pattern")
        self.assertIsNone(pattern)

if __name__ == '__main__':
    unittest.main()