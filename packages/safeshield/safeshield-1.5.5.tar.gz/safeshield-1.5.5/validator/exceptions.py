from typing import Dict, List, Tuple, Optional

class ValidationException(Exception):
    def __init__(self, errors: dict):
        self.errors = errors
        super().__init__(self.errors)
        
class RuleNotFoundException(ValueError):
    def __init__(self, rule_name: str):
        super().__init__(f"Validation rule '{rule_name}' is not registered")