from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from datetime import datetime
import zoneinfo
from dateutil.parser import parse

class DateRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
            
        try:
            parse(value)
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute is not a valid date."

class DateEqualsRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        
        try:
            if isinstance(value, str):
                date1 = parse(value)
            elif isinstance(value, datetime):
                date1 = value
            else:
                return False
            
            params = list(params)
            params[0] = self.get_field_value(params[0], params[0])
            
            date2 = parse(params[0])
            return date1 == date2
        except ValueError as e:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be equal to :value."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self.get_field_value(self._params[0], self._params[0])
        }
        
        return replacements
    
class AfterRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
                
            
            params = list(params)# Parse comparison date
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value > compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be after :value"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self.get_field_value(self._params[0], self._params[0])
        }
        
        return replacements
    
class AfterOrEqualRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params = list(params)
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value >= compare_date
            
        except (ValueError, TypeError) as e:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be after or equal to :value"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self.get_field_value(self._params[0], self._params[0])
        }
        
        return replacements
    
class BeforeRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        value = self.get_field_value(value, value)
    
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params = list(params)
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value < compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be before :value"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self.get_field_value(self._params[0], self._params[0])
        }
        
        return replacements
    
class BeforeOrEqualRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        value = self.get_field_value(value, value) 
        
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params = list(params)
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value <= compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be before or equal to :value"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':value': self.get_field_value(self._params[0], self._params[0])
        }
        
        return replacements
    
class DateFormatRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            datetime.strptime(value, params[0])
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must match the format :format"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':format': self.get_field_value(self._params[0], self._params[0])
        }
        
        return replacements
    
class TimezoneRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            zoneinfo.ZoneInfo(value)
            return True
        except zoneinfo.ZoneInfoNotFoundError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid timezone."