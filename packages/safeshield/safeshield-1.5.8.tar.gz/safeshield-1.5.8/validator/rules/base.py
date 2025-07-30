from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from enum import Enum
import inspect
import re

class Rule(ABC):
    """Abstract base class for all validation rules"""
    
    _rule_classes: Dict[str, Type['Rule']] = {}
    
    def __init__(self, *params: str):
        self._validator: Optional['Validator'] = None
        self._params: List[str] = list(params)
        
    def __init_subclass__(cls):
        cls.rule_name = cls.pascal_to_snake(cls.__name__) if not hasattr(cls, '_name') else cls._name
        cls._register_rule_class()
        cls._generate_rule_methods()
        
    @property
    def params(self):
        params = []
        for rule_set in self._params:
            if isinstance(rule_set, (list, tuple)):
                params.append(tuple(rule_set))
            else:
                params.append(rule_set)
        return tuple(params)
    
    @classmethod
    def _register_rule_class(cls):
        cls._rule_classes[cls.rule_name] = cls
    
    @classmethod
    def _generate_rule_methods(cls):
        for rule_name, rule_class in cls._rule_classes.items():
            @classmethod
            def method(cls, *params, rule_class=rule_class):
                return rule_class(*params)
            
            setattr(cls.__class__, rule_name, method)
            
    @classmethod
    def _require_parameter_count(self, count, params, rule):
        if getattr(rule, '_accept_closure', False) and (isinstance(params[0], bool) or callable(params[0])):
            return
        
        if count > len(params):
            raise ValueError(f"Validation rule {rule.rule_name} requires at least {count} parameter")
            
    @params.setter
    def params(self, value: List[str]) -> None:
        self._params = value
    
    def set_validator(self, validator: 'Validator') -> None:
        """Set the validator instance this rule belongs to."""
        self._validator = validator
        
    def set_field_exists(self, exists: bool):
        self._field_exists = exists
    
    @property
    def validator(self) -> 'Validator':
        """Get the validator instance."""
        if self._validator is None:
            raise RuntimeError("Validator not set for this rule!")
        return self._validator
    
    @property
    def field_exists(self):
        return self._field_exists
    
    def get_field_value(self, field_name, default=''):
        return str(self.validator.data.get(field_name, default))
    
    @staticmethod
    def is_empty(value):
        return value in (None, '', [], {})
    
    @abstractmethod
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        """Validate a field's value."""
        pass
    
    @abstractmethod
    def message(self, field: str) -> str:
        """Generate an error message if validation fails."""
        pass
    
    def replacements(self, field, value) -> Dict[str, str]:
        """Default replacements for all rules"""
        return {':attribute': self._get_display_name(field), 'value': value }
    
    def _get_display_name(self, fields: str) -> str:
        print(isinstance(fields, str), '3/33333333333333333333')
        single_input = isinstance(fields, str)
        if single_input:
            fields = [fields]
        
        attributes = []
        
        for field in fields:
            if field in self.validator.custom_attributes:
                attributes.append(self.validator.custom_attributes[field])
                continue
                
            parts = field.split('.')
            base_name = parts[-1].replace('_', ' ').title()
            
            for i in range(len(parts), 0, -1):
                wildcard = '.'.join(parts[:i]) + '.*'
                if wildcard in self.validator.custom_attributes:
                    attributes.append(self.validator.custom_attributes[wildcard])
                    break
            else:
                attributes.append(self.validator.custom_attributes.get(parts[-1], base_name))
        
        return attributes[0] if single_input else attributes
    
    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Return the name of the rule for error messages."""
        pass
    
    def _parse_option_values(self, field: str, params: List[str], raise_for_error=True) -> List[Any]:
        """Parse parameters into allowed values, supporting both Enum class and literal values"""
        
        if not params and raise_for_error:
            raise ValueError(
                f"{self.rule_name} rule requires parameters. "
                f"Use '({self.rule_name}, EnumClass)' or '{self.rule_name}:val1,val2'"
            )
            
        enum_params = [param for param in params if inspect.isclass(param) and issubclass(param, Enum)]
        params = [param for param in params if param not in enum_params]
        
        for enum_param in enum_params:
            params.extend([e.value for e in enum_param])
            
        params = set([str(param) for param in params])
            
        param_str = ' ,'.join(params)
        
        return [v.strip() for v in param_str.split(',') if v.strip()]
    
    def pascal_to_snake(name):
        """Convert PascalCase to snake_case"""
        # Handle kasus khusus terlebih dahulu
        special_cases = {
            'UUIDRule': 'uuid',
            'IPRule': 'ip',
            'URLRule': 'url'
        }
        if name in special_cases:
            return special_cases[name]
        
        # Konversi regular PascalCase ke snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return result.replace('_rule', '')