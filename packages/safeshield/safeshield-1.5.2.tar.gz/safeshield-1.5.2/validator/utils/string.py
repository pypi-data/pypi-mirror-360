import re

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