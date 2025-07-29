import inspect
from .base import Rule
from . import array, basic, comparison, date, files, format, boolean, string, numeric, utilities

def _collect_rules():
    modules = [array, basic, comparison, date, files, format, boolean, string, numeric, utilities]
    rules = {}
    
    for module in modules:
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, Rule) and 
                obj != Rule):
                rules[obj.rule_name] = obj
    return rules

all_rules = _collect_rules()

for name, cls in all_rules.items():
    globals()[cls.__name__.replace('Rule', '')] = cls  # Export class name
    globals()[name] = cls  # Export rule name


__all__ = ['Rule'] + [cls.__name__.replace('Rule', '') for cls in all_rules.values()]