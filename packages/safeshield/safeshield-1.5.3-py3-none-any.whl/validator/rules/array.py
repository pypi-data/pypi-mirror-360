from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

class ArrayRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if params:
            params = self._parse_option_values(self.rule_name, params)
            if not isinstance(value, dict):
                return False
            
            missing = [param for param in params if param not in value]
            return len(missing) == 0

        return isinstance(value, (list, tuple, set))

    def message(self, field: str, params: List[str]) -> str:
        if params:
            return f"The :attribute must contain the keys: :values."
        return f"The :attribute must be an array."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params)
        }
        
        return replacements
    
class DistinctRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, (list, tuple, set)):
            return False
            
        ignore_case = 'ignore_case' in params
        
        seen = set()
        for item in value:
            compare_val = item
            
            if ignore_case and isinstance(item, str):
                compare_val = item.lower()
            
            if compare_val in seen:
                return False
            seen.add(compare_val)
            
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        base_msg = f"The :attribute must contain unique values"
        
        if 'ignore_case' in params:
            return f"{base_msg} (case insensitive)"
        else:
            return f"{base_msg} (strict comparison)"
        
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0] if self._params else None
        }
        
        return replacements
    
class InArrayRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return str(value) in self.get_field_value(params[0], [])
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be one of: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self.get_field_value(self._params[0], []))
        }
        
        return replacements
    
class InArrayKeysRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, dict):
            return False
            
        return any(key in value for key in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must contain at least one of these keys: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params)
        }
        
        return replacements