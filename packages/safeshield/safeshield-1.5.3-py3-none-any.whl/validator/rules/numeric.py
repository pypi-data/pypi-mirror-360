from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
import decimal

class NumericRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, (int, float)):
            return True
        if not isinstance(value, str):
            return False
        return value.replace('.', '', 1).isdigit()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a number."
    
class IntegerRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, int):
            return True
        if not isinstance(value, str):
            return False
        return value.isdigit()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be an integer."

class DigitsRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            digits = int(params[0])
        except ValueError:
            return False
            
        return value.isdigit() and len(value) == digits
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be :value digits."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0],
        }
        
        return replacements

class DigitsBetweenRule(Rule):
    _count_parameter = 2
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            min_digits = int(params[0])
            max_digits = int(params[1])
        except ValueError:
            return False
            
        return value.isdigit() and min_digits <= len(value) <= max_digits
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be between :min and :max digits."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':min': self._params[0],
            ':max': self._params[1],
        }
        
        return replacements
    
class DecimalRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            decimal.Decimal(str(value))
            return True
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return "The :attribute must be a decimal number."

class GreaterThanRule(Rule):
    _name = 'gt'
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            threshold = decimal.Decimal(params[0])
            numeric_value = decimal.Decimal(str(value))
            return numeric_value > threshold
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be greater than :value."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0],
        }
        
        return replacements

class GreaterThanOrEqualRule(Rule):
    _name = 'gte'
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            threshold = decimal.Decimal(params[0])
            numeric_value = decimal.Decimal(str(value))
            return numeric_value >= threshold
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be greater than or equal to :value."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0],
        }
        
        return replacements

class LessThanRule(Rule):
    _name = 'lt'
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            threshold = decimal.Decimal(params[0])
            numeric_value = decimal.Decimal(str(value))
            return numeric_value < threshold
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be less than :value."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0],
        }
        
        return replacements

class LessThanOrEqualRule(Rule):
    _name = 'lte'
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            threshold = decimal.Decimal(params[0])
            numeric_value = decimal.Decimal(str(value))
            return numeric_value <= threshold
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be less than or equal to :value."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0],
        }
        
        return replacements

class MaxDigitsRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            max_digits = int(params[0])
            numeric_value = decimal.Decimal(str(value))
            str_value = str(numeric_value).replace("-", "")
            if '.' in str_value:
                str_value = str_value.replace(".", "")
            return len(str_value) <= max_digits
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must not exceed :value digits."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0],
        }
        
        return replacements

class MinDigitsRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            min_digits = int(params[0])
            numeric_value = decimal.Decimal(str(value))
            str_value = str(numeric_value).replace("-", "")
            if '.' in str_value:
                str_value = str_value.replace(".", "")
            return len(str_value) >= min_digits
        except (decimal.InvalidOperation, TypeError, ValueError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must have at least :value digits."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0],
        }
        
        return replacements

class MultipleOfRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            divisor = float(params[0])
            if divisor == 0:
                return False
            num = float(value)
            return num % divisor == 0
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a multiple of :value."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self._params[0]
        }
        
        return replacements