from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
import re

# =============================================
# STRING VALIDATION RULES
# =============================================

class StringRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a string."

class AlphaRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and value.isalpha()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute may only contain letters."

class AlphaDashRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and bool(re.match(r'^[a-zA-Z0-9_-]+$', value))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute may only contain letters, numbers, dashes and underscores."

class AlphaNumRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and value.isalnum()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute may only contain letters and numbers."

class UppercaseRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and value == value.upper()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be uppercase."

class LowercaseRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and value == value.lower()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be lowercase."

class AsciiRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and all(ord(c) < 128 for c in value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must only contain ASCII characters."
    
class StartsWithRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return any(value.startswith(p) for p in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must start with one of the following: :values."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params),
        }
        
        return replacements
    
class DoesntStartWithRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return all(not value.startswith(prefix) for prefix in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must not start with any of: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params),
        }
        
        return replacements

class EndsWithRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return any(value.endswith(p) for p in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must end with one of the following: :values."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params),
        }
        
        return replacements
    
class DoesntEndWithRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str) or not params:
            return False
        return all(not value.endswith(suffix) for suffix in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must not end with any of: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params),
        }
        
        return replacements
    
class ConfirmedRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        confirmation_field = f"{field}_confirmation"
        
        return value == self.get_field_value(confirmation_field, '') 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute confirmation does not match."
    
class RegexRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            return bool(re.fullmatch(params[0], value))
        except re.error:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute format is invalid."

class NotRegexRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            return not bool(re.search(params[0], value))
        except re.error:
            return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute format is invalid."