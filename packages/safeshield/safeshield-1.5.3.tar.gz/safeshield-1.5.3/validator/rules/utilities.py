from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from .basic import *
from .boolean import AcceptedRule, DeclinedRule

class RequiredIfRule(RequiredRule):
    _count_parameter = 2
    _accept_closure = True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:  
            expected_value = self.get_field_value(params[0], False)
            conditions = params[1:]
            
            condition_met = expected_value in conditions
                
        if condition_met:
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
            ':values': ', '.join(self._params[1:]),
        }
        
        return replacements
    
class RequiredUnlessRule(RequiredRule):
    _count_parameter = 2
    _accept_closure = True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:  
            expected_value = self.get_field_value(params[0], False)
            conditions = params[1:]
            
            condition_met = expected_value in conditions
                
        if not condition_met:
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
            ':values': ', '.join(self._params[1:]),
        }
        
        return replacements
    
class RequiredWithRule(RequiredRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(f in self.validator.data for f in params):
            return super().validate(field, value, params)
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements

class RequiredWithAllRule(RequiredRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if all(f in self.validator.data for f in params):
            return super().validate(field, value, params)
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements
    
class RequiredWithoutRule(RequiredRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(f not in self.validator.data for f in params):
            return super().validate(field, value, params)
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements
    
class RequiredWithoutAllRule(RequiredRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if all(f not in self.validator.data for f in params):
            return super().validate(field, value, params)
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements
    
class RequiredIfAcceptedRule(RequiredRule, AcceptedRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if AcceptedRule.validate(self, field, params[0], params):
            return super().validate(field, value, params)
        
        return True
    
class RequiredIfDeclinedRule(RequiredRule, DeclinedRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if DeclinedRule.validate(self, field, params[0], params):
            return super().validate(field, value, params)
        
        return True
    
class RequiredArrayKeysRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, dict):
            return False
        return all(key in value for key in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must contain all required keys: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            'values': ', '.join(self._params),
        }
        
        return replacements
    
class ProhibitedIfRule(ProhibitedRule):
    _count_parameter = 2
    _accept_closure = True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:    
            expected_value, conditions = self.get_field_value(params[0], None), params[1:]
            condition_met = expected_value in conditions
        
        if condition_met:
            return super().validate(field, value, params)
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
            ':values': ', '.join(self._params[1:]),
        }
        
        return replacements
    
class ProhibitedUnlessRule(ProhibitedRule):
    _count_parameter = 2
    _accept_closure = True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:  
            expected_value, conditions = self.get_field_value(params[0], None), params[1:]
            condition_met = expected_value in conditions
        
        if not condition_met:
            return super().validate(field, value, params)
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
            ':values': ', '.join(self._params[1:]),
        }
        
        return replacements
    
class ProhibitedIfAcceptedRule(ProhibitedRule, AcceptedRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if AcceptedRule.validate(self, field, params[0], params):
            return super().validate(field, value, params)
        return True

class ProhibitedIfDeclinedRule(ProhibitedRule, DeclinedRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if DeclinedRule.validate(self, field, params[0], params):
            return super().validate(field, value, params)
        
        return True
    
class PresentIfRule(PresentRule):
    _count_parameter = 2
    _accept_closure = True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:
            expected_value, conditions = self.get_field_value(params[0], None), params[1:]
            
            condition_met = expected_value in conditions
            
        if condition_met:
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
            ':values': ', '.join(self._params[1:]),
        }
        
        return replacements
    
class PresentUnlessRule(PresentRule):
    _count_parameter = 2
    _accept_closure = True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:
            expected_value, conditions = self.get_field_value(params[0], None), params[1:]
            
            condition_met = expected_value in conditions
            
        if not condition_met:
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
            ':values': ', '.join(self._params[1:]),
        }
        
        return replacements
    
class PresentWithRule(PresentRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(self.get_field_value(param, None) is not None for param in params):
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements
    
class PresentWithAllRule(PresentRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if all(self.get_field_value(param, None) is not None for param in params):
            return super().validate(field, value, params)
        
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements

class MissingIfRule(MissingRule):
    _count_parameter = 2
    _accept_closure = True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:
            expected_value, conditions = self.get_field_value(params[0], None), params[1:]
            condition_met = expected_value in conditions
            
        if condition_met:
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
            ':values': ', '.join(self._params[1:]),
        }
        
        return replacements
    
class MissingUnlessRule(MissingRule):
    _count_parameter = 2
    _accept_closure = True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:
            expected_value, conditions = self.get_field_value(params[0], None), params[1:]
            condition_met = expected_value in conditions
            
        if not condition_met:
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':other': self._get_display_name(self._params[0]),
            ':values': ', '.join(self._params[1:]),
        }
        
        return replacements
            
class MissingWithRule(MissingRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if any(self.get_field_value(param, None) is not None for param in params):
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements
    
class MissingWithAllRule(MissingRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        
        if all(self.get_field_value(param, None) is not None for param in params):
            return super().validate(field, value, params)
        
        return True
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params)),
        }
        
        return replacements
    
class ExcludeIfRule(ExcludeRule):
    _count_parameter = 2
    _accept_closure =  True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:
            expected_value, conditions = self.get_field_value(params[0], None), params[1:]
            condition_met = expected_value in conditions
        
        if condition_met:
            return super().validate(field, value, params)
        return True

class ExcludeUnlessRule(ExcludeRule):
    _count_parameter = 2
    _accept_closure =  True
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if callable(params[0]):
            condition_met = params[0](self.validator.data)
        elif isinstance(params[0], bool):
            condition_met = params[0]
        else:
            expected_value, conditions = self.get_field_value(params[0], None), params[1:]
            condition_met = expected_value in conditions
        
        if not condition_met:
            return super().validate(field, value, params)
        return True

class ExcludeWithRule(ExcludeRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(not self.is_empty(self.get_field_value(param, None)) for param in params):
            return super().validate(field, value, params)
            
        return True
    
class ExcludeWithoutRule(ExcludeRule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(self.is_empty(self.get_field_value(param, None)) for param in params):
            return super().validate(field, value, params)
            
        return True
