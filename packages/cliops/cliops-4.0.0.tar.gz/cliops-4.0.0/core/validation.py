from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, Union
import re

class StateSchema(BaseModel):
    ARCHITECTURE: str = Field(..., min_length=1, description="Project architecture")
    FOCUS: str = Field(..., min_length=1, description="Current project focus")
    PATTERNS: str = Field(..., min_length=1, description="Preferred patterns")
    DEFAULT_PATTERN: Optional[str] = Field(None, description="Default optimization pattern")

    @field_validator('ARCHITECTURE')
    @classmethod
    def validate_architecture(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Architecture must be at least 3 characters')
        return v.strip()

    @field_validator('PATTERNS')
    @classmethod
    def validate_patterns(cls, v):
        # Basic pattern name validation
        pattern_names = [p.strip() for p in v.split(',')]
        for name in pattern_names:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                raise ValueError(f'Invalid pattern name: {name}')
        return v

class PromptValidator:
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        if not text or not isinstance(text, str):
            raise ValueError("Input must be a non-empty string")
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'<[^>]*>', '', text.strip())  # Remove HTML tags
        sanitized = re.sub(r'[{}]', '', sanitized)  # Remove braces
        
        if len(sanitized) < 3:
            raise ValueError("Input too short (minimum 3 characters)")
        
        return sanitized

    @staticmethod
    def validate_pattern_name(name: str) -> str:
        """Validate pattern name"""
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            raise ValueError(f"Invalid pattern name: {name}")
        return name