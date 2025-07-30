# factory.py
from typing import Type, Dict, List, Any
from validator.rules import all_rules
from validator.rules.base import Rule

class RuleFactory:
    _rules: Dict[str, Type[Rule]] = all_rules
    
    @classmethod
    def create_rule(cls, rule_name: str) -> Rule:
        try:
            return cls._rules[rule_name]()
        except KeyError:
            raise ValueError(f"Unknown validation rule: {rule_name}")
    
    @classmethod
    def register_rule(cls, name: str, validate_func: callable, message_func: callable):
        class NewRule(Rule):
            _name = name
            
            def validate(self, field: str, value: Any, params: List[str]) -> bool:
                return validate_func(field, value, params)
            
            def message(self, field: str, params: List[str]) -> str:
                return message_func(field, params)
            
        cls._rules[name] = NewRule
        
    @classmethod
    def has_rule(cls, rule_name: str) -> bool:
        return rule_name in cls._rules

    @classmethod
    def get_rule_names(cls) -> List[str]:
        return list(cls._rules.keys())