import unittest
from core.validation import StateSchema, PromptValidator
from pydantic import ValidationError

class TestValidation(unittest.TestCase):
    def test_state_schema_valid(self):
        """Test valid state schema"""
        data = {
            "ARCHITECTURE": "React + Node.js",
            "FOCUS": "API development", 
            "PATTERNS": "context_aware_generation,bug_fix_precision"
        }
        schema = StateSchema(**data)
        self.assertEqual(schema.ARCHITECTURE, "React + Node.js")

    def test_state_schema_invalid(self):
        """Test invalid state schema"""
        with self.assertRaises(ValidationError):
            StateSchema(ARCHITECTURE="", FOCUS="test", PATTERNS="valid_pattern")

    def test_prompt_validator_sanitize(self):
        """Test prompt sanitization"""
        validator = PromptValidator()
        
        # Valid input
        result = validator.sanitize_input("Create a function")
        self.assertEqual(result, "Create a function")
        
        # Input with dangerous characters
        result = validator.sanitize_input("Create <script>alert()</script> function")
        self.assertEqual(result, "Create alert() function")
        
        # Invalid input
        with self.assertRaises(ValueError):
            validator.sanitize_input("")
        
        with self.assertRaises(ValueError):
            validator.sanitize_input("ab")  # Too short

    def test_pattern_name_validation(self):
        """Test pattern name validation"""
        validator = PromptValidator()
        
        # Valid names
        self.assertEqual(validator.validate_pattern_name("valid_pattern"), "valid_pattern")
        self.assertEqual(validator.validate_pattern_name("pattern123"), "pattern123")
        
        # Invalid names
        with self.assertRaises(ValueError):
            validator.validate_pattern_name("invalid-pattern")
        
        with self.assertRaises(ValueError):
            validator.validate_pattern_name("123invalid")

if __name__ == '__main__':
    unittest.main()