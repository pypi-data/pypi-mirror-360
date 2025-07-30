from typing import Dict, List, Any, Optional, Union
import re

class RuleErrorHandler:
    def __init__(self, messages: Dict[str, str] = None, custom_attributes: Dict[str, str] = None):
        self.messages = messages or {}
        self.custom_attributes = custom_attributes or {}
        self.errors: Dict[str, List[str]] = {}
        self._current_rule: Optional[str] = None
        self._current_params: Optional[List[str]] = None
        self._current_value: Optional[Any] = None

    def add_error(self, field: str, rule: Any, rule_params: List[str], default_message: str, value: Any) -> None:
        """Add error message with support for all parameter formats"""
        self._current_rule = rule
        self._current_params = rule_params
        self._current_value = value
        
        message = self._format_message(field, rule, default_message, value)
        self.errors.setdefault(field, []).append(message)

    def _format_message(self, field: str, rule: Any, default_message: str, value: Any) -> str:
        message = self._select_message(field, rule.rule_name, field, default_message)
        return self._replace_placeholders(message, rule.replacements(field, value))

    def _stringify(self, value: Any) -> str:
        """Convert value to display string"""
        if value is None:
            return None
        if isinstance(value, (list, dict, set)):
            return ', '.join(str(v) for v in value) if value else 'none'
        return str(value)

    def _select_message(self, field: str, rule_name: str, attribute: str, default: str) -> str:
        """Select the most specific error message available"""
        return (
            self.messages.get(f"{field}.{rule_name}") or
            self.messages.get(field) or
            self.messages.get(rule_name) or
            default
        )
        
    def _replace_placeholders(self, message: str, replacements: Dict[str, str]) -> str:
        """Safely replace all placeholders in message"""
        for ph, val in replacements.items():
            if val:
                message = message.replace(ph, self._stringify(val))
        return message

    @property
    def has_errors(self) -> bool:
        """Check if any validation errors exist"""
        return bool(self.errors)