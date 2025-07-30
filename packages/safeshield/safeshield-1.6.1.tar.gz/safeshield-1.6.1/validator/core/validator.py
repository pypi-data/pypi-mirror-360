from typing import Optional, Dict, Any, List, Tuple, Union
from validator.exceptions import ValidationException, RuleNotFoundException
from validator.factory import RuleFactory
from validator.database import DatabaseManager, DatabaseAutoDetector
from validator.rules import Rule
from validator.services.rule_conflict import RuleConflictChecker
from validator.services.rule_error_handler import RuleErrorHandler
from validator.services.rule_preparer import RulePreparer
import warnings
from collections.abc import Mapping

class Validator:
    """Main validation class with proper abstractions"""
    PRIORITY_RULES = {
        'bail', 'sometimes', 'dynamic', 'exclude', 'exclude_unless', 'exclude_if', 'exclude_with', 'exclude_without', 'required', 'required_if', 'required_unless',
        'required_with', 'required_without'
    }

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        rules: Optional[Dict[str, Union[
            str, 
            List[Union[
                str, 
                Rule, 
                Tuple[str, Union[
                    str, 
                    Union[
                        Tuple[str], 
                        List[str]
                    ], 
                    Union[
                        Tuple[str], 
                        List[str]
                    ]
                ]]
            ]],
            Tuple[Union[
                str, 
                Rule, 
                Tuple[str, Union[
                    str, 
                    Union[
                        Tuple[str], 
                        List[str]
                    ], 
                    Union[
                        Tuple[str], 
                        List[str]
                    ]
                ]]
            ]]
        ]]] = None,
        messages: Optional[Dict[str, str]] = None,
        custom_attributes: Optional[Dict[str, str]] = None,
        db_config: Optional[Dict[str, Any]] = None,
        # rule_preparer: Optional[RulePreparer] = None,
        # error_handler: Optional[RuleErrorHandler] = None
    ):
        self.data = data or {}
        self._raw_rules = rules or {}
        self.prepared_rules = None
        self._stop_on_first_failure = False
        self._field_to_exclude = []
        
        
        # Initialize dependencies
        self.rule_preparer = RulePreparer(RuleFactory())
        self.error_handler = RuleErrorHandler(messages, custom_attributes)
        self.custom_attributes = custom_attributes or {}
        
        # Database configuration
        self.db_config = db_config or DatabaseAutoDetector.detect()
        if not self.db_config:
            warnings.warn(
                "No database config detected. exists/unique validations will be skipped!",
                RuntimeWarning
            )
        self.db_manager = DatabaseManager(self.db_config) if self.db_config else None

    def validate(self) -> bool:
        """Validate the data against the rules"""
        self.prepared_rules = self.rule_preparer.prepare(self._raw_rules)
        self.error_handler.errors.clear()
        
        validated = self._validate_rules(self.prepared_rules, priority_only=True)
        
        # First pass: priority rules
        if self.error_handler.has_errors and self._stop_on_first_failure:
            return False
        
        # Second pass: remaining rules
        self._validate_rules(self.prepared_rules, priority_only=False)
        
        if self.error_handler.has_errors:
            return False
        
        return self.data

    def _validate_rules(self, prepared_rules: Dict[str, List[Rule]], priority_only: bool):
        validated = []
        for field_pattern, rules in prepared_rules.items():
            concrete_paths = self._resolve_wildcard_paths(field_pattern) if '*' in field_pattern else [field_pattern]
            
            for actual_path in concrete_paths:
                self._current_actual_path = actual_path
                raw_values = self._get_nested_value(actual_path)
                field_exists = self._field_exists_in_data(actual_path)
                
                # Handle empty array case for wildcard
                is_wildcard = '*' in field_pattern
                is_empty_array = isinstance(raw_values, list) and len(raw_values) == 0
                
                # Special case: wildcard path with empty array
                if is_wildcard and is_empty_array:
                    values_to_validate = []
                elif not is_wildcard and not is_empty_array:
                    values_to_validate = [raw_values]
                else:
                    values_to_validate = [None] if not field_exists else (
                        [raw_values] if not isinstance(raw_values, list) else raw_values
                    )
                    
                for rule in rules:
                    if priority_only == (rule.rule_name in self.PRIORITY_RULES):
                        rule.set_field_exists(field_exists)
                        
                        # Skip validation for empty array with wildcard unless it's a required rule
                        if is_wildcard and is_empty_array and rule.rule_name != 'required':
                            continue
                            
                        for value in values_to_validate:
                            if field_pattern not in self._field_to_exclude:
                                validated.append(self._apply_rule(field_pattern, value, rule))
                
                delattr(self, '_current_actual_path')
                
        return all(valid for valid in validated)
    
    def _resolve_wildcard_paths(self, pattern: str) -> List[str]:
        parts = pattern.split('.')
        
        def _resolve(data: Any, current_path: str, remaining_parts: List[str]) -> List[str]:
            if not remaining_parts:
                return [current_path] if current_path else []
            
            part = remaining_parts[0]
            next_parts = remaining_parts[1:]
            
            if part == '*':
                results = []
                # Kasus khusus: wildcard di akhir path
                if not next_parts:
                    if isinstance(data, (list, tuple)):
                        for i in range(len(data)):
                            new_path = f"{current_path}.{i}" if current_path else str(i)
                            results.append(new_path)
                    elif isinstance(data, dict):
                        for key in data.keys():
                            new_path = f"{current_path}.{key}" if current_path else key
                            results.append(new_path)
                    else:
                        # Jika bukan collection, kembalikan path saat ini
                        if current_path:
                            results.append(current_path)
                    return results
                
                # Wildcard di tengah path (seperti sebelumnya)
                if isinstance(data, (list, tuple)):
                    for i, item in enumerate(data):
                        new_path = f"{current_path}.{i}" if current_path else str(i)
                        results.extend(_resolve(item, new_path, next_parts))
                elif isinstance(data, dict):
                    for key, value in data.items():
                        new_path = f"{current_path}.{key}" if current_path else key
                        results.extend(_resolve(value, new_path, next_parts))
                return results
            
            # Handle regular path (sama seperti sebelumnya)
            next_data = None
            if isinstance(data, dict) and part in data:
                next_data = data[part]
            elif isinstance(data, (list, tuple)) and part.isdigit():
                index = int(part)
                if 0 <= index < len(data):
                    next_data = data[index]
            
            if next_data is not None:
                new_path = f"{current_path}.{part}" if current_path else part
                return _resolve(next_data, new_path, next_parts)
            
            return []
    
        return _resolve(self.data, '', parts)
    
    def _field_exists_in_data(self, field_path: str) -> bool:
        parts = field_path.split('.')
        
        def _check(data: Any, remaining_parts: List[str]) -> bool:
            if not remaining_parts:
                return True
                
            part = remaining_parts[0]
            next_parts = remaining_parts[1:]
            
            if part == '*':
                if isinstance(data, (list, tuple)):
                    return any(_check(item, next_parts) for item in data)
                elif isinstance(data, dict):
                    return any(_check(value, next_parts) for value in data.values())
                return False
            
            if isinstance(data, dict) and part in data:
                return _check(data[part], next_parts)
            elif isinstance(data, (list, tuple)) and part.isdigit():
                index = int(part)
                return 0 <= index < len(data) and _check(data[index], next_parts)
            
            return False
        
        return _check(self.data, parts)
    
    def _apply_rule(self, field: str, value: Any, rule: Rule) -> bool:
        rule.set_validator(self)
            
        display_field = getattr(self, '_current_actual_path', field)
        rule._require_parameter_count(getattr(rule, '_count_parameter', 0), getattr(rule, 'params', []), rule)
            
        if not rule.validate(field, value, getattr(rule, 'params', [])):
            msg = rule.message(display_field, getattr(rule, 'params', []))
            self.error_handler.add_error(display_field, rule, getattr(rule, 'params', []), msg, value)
            
            return False
        else:
            return True

    def _get_nested_value(self, path: str) -> Any:
        parts = path.split('.')
        
        def _get(data: Any, remaining_parts: List[str]) -> Any:
            if not remaining_parts:
                return data
                
            part = remaining_parts[0]
            next_parts = remaining_parts[1:]
            
            if part == '*':
                if isinstance(data, (list, tuple)):
                    return [_get(item, next_parts) for item in data]
                elif isinstance(data, dict):
                    return [_get(value, next_parts) for value in data.values()]
                return None
            
            if isinstance(data, dict) and part in data:
                return _get(data[part], next_parts)
            elif isinstance(data, (list, tuple)) and part.isdigit():
                index = int(part)
                if 0 <= index < len(data):
                    return _get(data[index], next_parts)
            
            return None
        
        result = _get(self.data, parts)
        
        # Flatten only one level for wildcard results
        if isinstance(result, list):
            flat_result = []
            for item in result:
                if isinstance(item, list):
                    flat_result.extend(item)
                elif item is not None:
                    flat_result.append(item)
            return flat_result if flat_result else None
        
        return result
    
    def add_rule(self, field: str, rules: Union[str, List[Union[str, Rule]], Rule]):
        """Add new rules to a field"""
        new_rules = self.rule_preparer._convert_to_rules(rules)
        existing_rules = self.rule_preparer._convert_to_rules(self._raw_rules.get(field, []))
        combined_rules = existing_rules + new_rules
        
        RuleConflictChecker.check_conflicts(combined_rules)
        self._raw_rules[field] = self.rule_preparer._deduplicate_rules(field, combined_rules)

    def set_stop_on_first_failure(self, value: bool) -> None:
        """Set whether to stop validation after first failure"""
        self._stop_on_first_failure = value

    @property
    def errors(self) -> Dict[str, List[str]]:
        """Get current validation errors"""
        return self.error_handler.errors
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any validation errors"""
        return self.error_handler.has_errors