from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type, Callable

# =============================================
# COMPARISON VALIDATION RULES
# =============================================

class MinRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            min_val = float(params[0])
        except ValueError:
            return False
            
        if isinstance(value, (int, float)):
            return value >= min_val
        elif isinstance(value, str):
            try:
                return len(value) >= min_val
            except ValueError:
                return len(value) >= min_val
        elif isinstance(value, (list, dict, set)):
            return len(value) >= min_val
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be at least :min."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':min': self._params[0],
        }
        
        return replacements

class MaxRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            max_val = float(params[0])
            
            # Handle Werkzeug/Flask FileStorage
            if hasattr(value, 'content_length'):  # Flask/Werkzeug
                file_size = value.content_length
                return file_size <= max_val
                
            # Handle generic file objects with size attribute
            if hasattr(value, 'size'):
                file_size = value.size
                return file_size <= max_val
                
            # Handle file-like objects with seek/read
            if hasattr(value, 'seek') and hasattr(value, 'read'):
                try:
                    current_pos = value.tell()
                    value.seek(0, 2)  # Seek to end
                    file_size = value.tell()
                    value.seek(current_pos)  # Return to original position
                    return file_size <= max_val
                except (AttributeError, IOError):
                    pass

            # Numeric validation
            if isinstance(value, (int, float)):
                return value <= max_val
                
            # String/collection length validation
            if isinstance(value, (str, list, dict, set, tuple)):
                length = len(value)
                return length <= max_val
                
            # String numeric validation
            if isinstance(value, str):
                try:
                    num = float(value)
                    return num <= max_val
                except ValueError:
                    length = len(value)
                    return length <= max_val
                    
        except (ValueError, TypeError) as e:
            return False
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        value = self.get_field_value(field)
        if value is None:
            return f"The :attribute must not exceed :max"
            
        # Check all possible file size attributes
        file_attrs = ['content_length', 'size', 'fileno']
        if any(hasattr(value, attr) for attr in file_attrs):
            return f"File :attribute must not exceed :max bytes"
        return f"The :attribute must not exceed :max"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':max': self._params[0],
        }
        
        return replacements

class BetweenRule(Rule):
    _count_parameter = 2
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            min_val = float(params[0])
            max_val = float(params[1])
            
            # File size validation (untuk Werkzeug/FileStorage)
            if hasattr(value, 'content_length'):  # Cek atribut Werkzeug
                file_size = value.content_length
                return min_val <= file_size <= max_val
            elif hasattr(value, 'size'):  # Cek atribut umum
                file_size = value.size
                return min_val <= file_size <= max_val
                
            # Numeric validation
            if isinstance(value, (int, float)):
                return min_val <= value <= max_val
                
            # String/collection length validation
            if isinstance(value, (str, list, dict, set, tuple)):
                length = len(value)
                return min_val <= length <= max_val
                
            # String numeric validation
            if isinstance(value, str):
                try:
                    num = float(value)
                    return min_val <= num <= max_val
                except ValueError:
                    length = len(value)
                    return min_val <= length <= max_val
                    
        except (ValueError, TypeError) as e:
            return False
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        value = self.get_field_value(field)
        if hasattr(value, 'content_length') or hasattr(value, 'size'):
            return f"File :attribute must be between :min and :max bytes"
        return f"The :attribute must be between :min and :max"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':min': self._params[0],
            ':max': self._params[1],
        }
        
        return replacements

class SizeRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            target_size = float(params[0])
            
            # 1. Handle file objects (Flask/Werkzeug/FastAPI)
            if hasattr(value, 'content_length'):  # Flask/Werkzeug
                return value.content_length == target_size
            elif hasattr(value, 'size'):  # FastAPI or custom file objects
                return value.size == target_size
            elif hasattr(value, 'seek') and hasattr(value, 'tell'):  # File-like objects
                current_pos = value.tell()
                value.seek(0, 2)  # Seek to end
                file_size = value.tell()
                value.seek(current_pos)  # Return to original position
                return file_size == target_size
                
            # 2. Handle numeric values
            if isinstance(value, (int, float)):
                return value == target_size
                
            # 3. Handle strings and collections
            if isinstance(value, (str, list, dict, set, tuple)):
                return len(value) == target_size
                
            # 4. Handle string representations of numbers
            if isinstance(value, str):
                try:
                    return float(value) == target_size
                except ValueError:
                    return len(value) == target_size
                    
        except (ValueError, TypeError, AttributeError) as e:
            return False
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        value = self.get_field_value(field)
        if value is None:
            return f"The :attribute must be exactly :size"
            
        # Check for file attributes
        file_attrs = ['content_length', 'size', 'fileno']
        if any(hasattr(value, attr) for attr in file_attrs):
            return f"File :attribute must be exactly :size bytes"
            
        return f"The :attribute must be exactly :size"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':size': self._params[0],
        }
        
        return replacements

class UniqueRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not hasattr(self.validator, 'db_manager') or not self.validator.db_manager:
            return False
            
        table = params[0]
        column = field if len(params) == 1 else params[1]
        
        try:
            ignore_id = None
            if len(params) > 2 and params[2].startswith('ignore:'):
                ignore_field = params[2].split(':')[1]
                ignore_id = self.get_field_value(ignore_field) 
            return self.validator.db_manager.is_unique(table, column, value, ignore_id)
        except Exception as e:
            print(f"Database error in UniqueRule: {e}")
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute has already been taken."

class ExistsRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not hasattr(self.validator, 'db_manager') or not self.validator.db_manager:
            return False
            
        table = params[0]
        column = field if len(params) == 1 else params[1]
        
        try:
            return self.validator.db_manager.exists(table, column, value)
        except Exception as e:
            print(f"Database error in ExistsRule: {e}")
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The selected :attribute is invalid."
    
class SameRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value == self.get_field_value(params[0], None) 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute and :other must match."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
        }
        
        return replacements

class DifferentRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        return str(value) != self.get_field_value(params[0]) 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute and :other must be different."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
        }
        
        return replacements

class InRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        allowed_values = self._parse_option_values(field, params)
        return (str(value) in allowed_values or value in allowed_values)

    def message(self, field: str, params: List[str]) -> str:
        return f"The selected :attribute must be in : :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements

class NotInRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return not InRule.validate(self, field, value, params=params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The selected :attribute must be not in : :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements
    
class EnumRule(Rule):
    _count_parameter = 1
    
    def __init__(self, *params):
        super().__init__()
        self._params: List[str] = list(params)
        self.allowed_values = self._parse_option_values(None, self._params, raise_for_error=False)
    
    def exclude(self, *options):
        except_values = self._parse_option_values(None, options, raise_for_error=False)
        self.allowed_values = [value for value in self.allowed_values if value not in except_values]
        return self
    
    def only(self, *options):
        only_values = self._parse_option_values(None, options, raise_for_error=False)
        self.allowed_values = [value for value in self.allowed_values if value in only_values]
        return self
    
    def when(self, 
            condition: bool, 
            when_true: Callable[['EnumRule'], 'EnumRule'], 
            when_false: Optional[Callable[['EnumRule'], 'EnumRule']] = None
        ) -> 'EnumRule':
        
        if condition:
            return when_true(self)
        elif when_false:
            return when_false(self)
        return self
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return (str(value) in self.allowed_values or value in self.allowed_values)

    def message(self, field: str, params: List[str]) -> str:
        allowed_values = self._parse_option_values(field, self.allowed_values)
        return f"The :attribute must be one of: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(map(str, self.allowed_values)),
        }
        
        return replacements
    
class ContainsRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        for search_value in params:
            if isinstance(value, str) and search_value in value:
                return True
                
            if isinstance(value, (int, float)) and str(search_value) in str(value):
                return True
                
            if isinstance(value, (list, tuple, set)) and search_value in value:
                return True
                
            if isinstance(value, dict) and search_value in value.keys():
                return True
                
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must contain at least one of: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params),
        }
        
        return replacements