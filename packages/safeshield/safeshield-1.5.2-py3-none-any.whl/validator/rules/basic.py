from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

# =============================================
# BASIC VALIDATION RULES
# =============================================

class AnyOfRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self._last_failed_rules = []
        
        for i, rule_set in enumerate(params):
            if isinstance(rule_set, str):
                rule_set = [rule_set]
            
            from validator import Validator
            
            temp_validator = Validator(
                {field: value},
                {field: rule_set},
                db_config=getattr(self._validator, 'db_config', None)
            )
            
            if temp_validator.validate():
                return True
            else:
                self._last_failed_rules.append({
                    'rules': rule_set,
                    'errors': temp_validator.errors.get(field, [])
                })
                
        return False
        
    def message(self, field: str, params: List[str]) -> str:
        if not self._last_failed_rules:
            return f"The :attribute field is invalid."
        
        error_messages = []
        
        for i, failed in enumerate(self._last_failed_rules, 1):
            rules_str = "|".join(
                r if isinstance(r, str) else getattr(r, 'rule_name', str(r))
                for r in failed['rules']
            )
            
            sub_errors = []
            for j, err_msg in enumerate(failed['errors'], 1):
                sub_errors.append(f"  {j}. {err_msg}")
            
            error_messages.append(
                f"Option {i} (Rules: {rules_str}):\n" + 
                "\n".join(sub_errors)
            )
        
        return (
            f"The :attribute must satisfy at least one of these conditions:\n" +
            "\n".join(error_messages)
        )
        
class WhenRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        rules = [rule for rule in self.validator.prepared_rules.get(field, []) if rule.rule_name != 'when']
        rules = [new_rule for new_rule in self.validator.rule_preparer._generate_rule(field, self._select_rules(field))]
        self.validator.prepared_rules[field] += rules
        
        return True

    def _select_rules(self, field: str) -> List[str]:
        selected = None
        for check_field, rules_map in self._params[0].items():
            current_value = str(self.get_field_value(check_field)) if self.get_field_value(check_field) is not None else ''
            for expected_value, rules in rules_map.items():
                if current_value == expected_value or expected_value == '*':
                    selected = rules
                    break
                
        return selected
    
    def message(self, field: str, params: List[str]) -> str:
        return ""

class BailRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self.validator._stop_on_first_failure = True
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""

class RequiredRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return not self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field is required."

class ProhibitedRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return "The :attribute field is must be empty."
    
class NullableRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute may be null."

class FilledRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return value not in ('', None)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must have a value."

class PresentRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return field in self.validator.data
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must be present."
    
class MissingRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return value is None
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute field must be missing."
    
class ProhibitsRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if value is None or value == '':
            return True
            
        for param in params:
            other_value = self.get_field_value(param, None)
            if other_value in self.validator.data:
                return False
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"When :attribute is present, :others must be empty or absent."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':others': ', '.join(self._get_display_name(self._params))
        }
        
        return replacements

class SometimesRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if value is None:
            self.validator._field_to_exclude.append(field)
            
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""
    
class ExcludeRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self.validator._field_to_exclude.append(field)
        
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""