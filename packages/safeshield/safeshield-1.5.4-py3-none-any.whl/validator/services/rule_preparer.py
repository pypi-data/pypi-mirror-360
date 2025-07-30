from validator.factory import RuleFactory
from validator.services.rule_conflict import RuleConflictChecker
from validator.rules import Rule
from typing import Dict, List, Union, Tuple
from validator.exceptions import RuleNotFoundException
from collections.abc import Iterable, Sequence
from numbers import Number
from enum import Enum
import inspect
import warnings

class RulePreparer:
    """Handles rule preparation and parsing"""
    def __init__(self, rule_factory: RuleFactory):
        self.rule_factory = rule_factory
        self.added_rules = {}

    def prepare(self, raw_rules: Dict[str, Union[str, List[Union[str, Rule]]]]) -> Dict[str, List[Rule]]:
        """Convert raw rules to prepared validation rules"""
        prepared_rules = {}
        for field, rule_input in raw_rules.items():
            if not rule_input:
                continue
            
            prepared_rules[field] = self._generate_rule(field, rule_input)
                
        return prepared_rules
    
    def _generate_rule(self, field, rule_input):
        rules = self._convert_to_rules(rule_input)
        RuleConflictChecker.check_conflicts(rules)
        
        return self._deduplicate_rules(field, rules)

    def _convert_to_rules(self, rule_input: Union[str, List[Union[str, Rule]], Rule, Tuple[Union[str, Rule], str], Tuple[Union[str, Rule], str]]) -> List[Rule]:
        """Convert mixed rule input to list of Rule objects"""
        if rule_input is None:
            return []
        if isinstance(rule_input, Rule):
            return [rule_input]
        if isinstance(rule_input, list | tuple):
            rules = []
            for r in rule_input:
                if isinstance(r, str):
                    rules.extend(self._parse_rule_string(r))
                elif isinstance(r, Rule):
                    rules.append(r)
                elif isinstance(r, (tuple, list)):
                    if len(r) == 0:
                        continue
                    try:
                        # Handle tuple/list format
                        rule_name = r[0]
                        params = r[1:] if len(r) > 1 else []
                        params = self._parse_params(params)
                        
                        if isinstance(rule_name, str):
                            rule = RuleFactory.create_rule(rule_name)
                            rule.params = params
                        elif isinstance(rule_name, Rule):
                            rule = rule_name
                            if params:
                                warnings.warn(f"Parameters {params} are ignored for Rule instance")
                        else:
                            raise ValueError(f"Invalid rule name type in {r}")
                            
                        rules.append(rule)
                    except Exception as e:
                        raise ValueError(f"Invalid rule format {r}: {str(e)}")   
            return rules
        if isinstance(rule_input, str):
            return self._parse_rule_string(rule_input)
        raise ValueError(f"Invalid rule input type: {type(rule_input)}")

    def _parse_rule_string(self, rule_str: str) -> List[Rule]:
        """Parse rule string into Rule objects"""
        rules = []
        for rule_part in rule_str.split('|'):
            rule_part = rule_part.strip()
            if not rule_part:
                continue
            rule_name, params = self._parse_rule_part(rule_part)
            try:
                rule = self.rule_factory.create_rule(rule_name)
                if params:
                    rule.params = params
                rules.append(rule)
            except RuleNotFoundException as e:
                warnings.warn(str(e))
        return rules

    def _parse_rule_part(self, rule_part: str) -> Tuple[str, List[str]]:
        """Parse single rule part into name and parameters"""
        if ':' not in rule_part:
            return rule_part, []
        rule_name, param_str = rule_part.split(':', 1)
            
        if rule_name in {'regex', 'not_regex', 'dimensions'}:
            return rule_name, [param_str]
        return rule_name, [p.strip() for p in param_str.split(',') if p.strip()]
    
    def _parse_params(self, params: Union[Tuple, List, str, Enum]):
        return set(tuple(x) if isinstance(x, list) else x for x in params)

    def _deduplicate_rules(self, field: str, rules: List[Rule]) -> List[Rule]:
        """Remove duplicate rules based on name and parameters"""
        unique = []
        for rule in rules:
            identifier = (rule.rule_name, tuple(rule.params))
            if rule.rule_name != 'when':
                if identifier not in self.added_rules.get(field, []):
                    if isinstance(self.added_rules.get(field), set):
                        self.added_rules[field].add(identifier)
                    else:
                        self.added_rules[field] = set()
                        self.added_rules[field].add(identifier)
                        
                    unique.append(rule)
            else:
                unique.append(rule)
        return unique