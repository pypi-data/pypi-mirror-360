from typing import List, Set, Dict, Tuple
import warnings

class RuleConflictChecker:
    """Class untuk mendeteksi dan menangani konflik antar validation rules."""
    
    CRITICAL_CONFLICTS = [
        ('required', 'nullable'),      # Cannot be both mandatory and optional
        ('required', 'sometimes'),     # Sometimes overrides required
        ('filled', 'prohibited'),      # Cannot require and prohibit simultaneously
        ('present', 'missing'),        # Field can't be both present and missing
        ('accepted', 'declined'),      # Values must be opposite
        ('same', 'different'),         # Direct logical opposites
        
        ('required', 'nullable'),      # Cannot be both mandatory and optional
        ('required', 'sometimes'),     # Sometimes overrides required
        ('filled', 'prohibited'),      # Cannot require and prohibit simultaneously
        ('present', 'missing'),        # Field can't be both present and missing
        ('accepted', 'declined'),      # Values must be opposite
        ('same', 'different'),         # Direct logical opposites
        
        # Numeric vs Other Types
        ('numeric', 'array'),
        ('numeric', 'boolean'),
        ('numeric', 'email'),
        ('numeric', 'date'),
        
        # String vs Other Types
        ('string', 'array'),
        ('string', 'file'),
        ('string', 'json'),
        
        # Special Types
        ('boolean', 'integer'),
        ('file', 'image'),            # All images are files but not vice versa
        ('uuid', 'ulid'),             # Similar but incompatible formats
        ('hex', 'alpha_num'),   
            
        # Email/URL/IP Conflicts
        ('email', 'ip'),
        ('email', 'url'),
        ('url', 'json'),
        
        # Date/Time Conflicts
        ('date', 'timezone'),
        ('date_format', 'date_equals'),
        ('after', 'before'),          # Illogical date ranges
        
        # Special Formats
        ('regex', 'not_regex'),       # Direct pattern negation
        ('ascii', 'alpha_dash'),      # ASCII vs extended charset
        ('uppercase', 'lowercase'),   # Case transformation conflicts
        
        # Direct Value Checks
        ('in', 'not_in'),
        ('starts_with', 'doesnt_start_with'),
        ('ends_with', 'doesnt_end_with'),
        
        # Range Conflicts
        ('between', 'digits_between'),
        ('min', 'gt'),
        ('max', 'lt'),
        ('size', 'max_digits'),
        
        # Numeric Constraints
        ('multiple_of', 'digits_between'),
        ('integer', 'decimal'),
        
        # Required Group
        ('required_if', 'exclude_if'),
        ('required_unless', 'exclude_unless'),
        
        # Presence Group
        ('present_if', 'missing_if'),
        ('present_unless', 'missing_unless'),
        
        # Acceptance Group
        ('accepted_if', 'declined_if'),
        ('accepted_unless', 'declined_unless'),
        
        # Prohibited Group
        ('prohibited_if', 'required_if'),
        ('prohibited_unless', 'required_unless'),
        
        ('file', 'dimensions'),       # Dimensions only for images
        ('image', 'mime_types'),
        ('extensions', 'mimes'),
        ('file', 'json'),             # Can't be both file and JSON
        
        ('array', 'distinct'),        # Distinct requires array
        ('in_array', 'contains'),     # Similar containment checks
        ('array_keys', 'in_array'),
    ]
    
    WARNING_CONFLICTS = [
        ('integer', 'numeric'),          # integer implies numeric check
        ('digits', 'digits_between'),    # digits:5 is same as digits_between:5,5
        ('decimal', 'numeric'),          # decimal is subset of numeric
        ('multiple_of', 'numeric'),      # multiple_of requires numeric
        ('min', 'gt'),         # similar lower-bound checks
        ('max', 'lt'),            # similar upper-bound checks
        ('digits_between', 'between'),   # overlapping digit vs value ranges
        
        ('alpha', 'alpha_num'),          # alpha_num includes alpha
        ('alpha_dash', 'alpha_num'),     # alpha_dash extends alpha_num
        ('ascii', 'alpha'),              # alpha implies ASCII
        ('uppercase', 'lowercase'),      # mutually exclusive cases
        ('starts_with', 'ends_with'),    # potentially redundant patterns
        ('regex', 'ascii'),              # regex might duplicate ASCII check
        ('contains', 'in_array'),        # similar containment checks
        
        ('after', 'after_or_equal'),     # _or_equal is more inclusive
        ('before', 'before_or_equal'),   # _or_equal is more inclusive
        ('date_format', 'date'),         # date implies format validation
        ('timezone', 'date_format'),     # timezone implies format
        ('date_equals', 'after_or_equal'),  # potential overlap
        
        ('file', 'image'),               # image implies file check
        ('mime_types', 'mime_type_by_extension'),  # similar type checks
        ('dimensions', 'image'),         # dimensions requires image
        
        ('array', 'distinct'),           # distinct requires array
        ('in_array', 'contains'),        # similar element checks
        ('array_keys', 'in_array'),      # similar key existence checks
        
        ('required_if', 'required_with'),        # similar conditional logic
        ('prohibited_if', 'prohibited_unless'),  # inverse conditions
        ('present_with', 'missing_with'),        # mutually aware rules
        
        ('string', 'alpha'),            # string conversion implied
        ('numeric', 'integer'),         # numeric conversion implied
        ('boolean', 'accepted'),        # boolean conversion implied
    ]
    
    REQUIRED_GROUPS = {
        'required_if', 'required_unless', 'required_with', 'required_with_all',
        'required_without', 'required_without_all', 'required_if_accepted', 'required_if_declined'
    }

    PROHIBITED_GROUPS = {
        'prohibited_if', 'prohibited_unless', 'prohibited_if_accepted', 'prohibited_if_declined'
    }

    EXCLUSION_GROUPS = {
        'exclude_if', 'exclude_unless', 'exclude_with', 'exclude_without'
    }

    PRESENCE_GROUPS = {
        'present_if', 'present_unless', 'present_with', 'present_with_all',
        'missing_if', 'missing_unless', 'missing_with', 'missing_with_all'
    }

    @classmethod
    def check_conflicts(cls, rules: List['Rule']) -> None:
        rule_names = {r.rule_name for r in rules}
        params_map = {r.rule_name: r.params for r in rules}
        
        cls._check_critical_conflicts(rule_names)
        cls._check_warning_conflicts(rule_names)
        cls._check_parameter_conflicts(rule_names, params_map)
        cls._check_special_cases(rule_names)

    @classmethod
    def _check_critical_conflicts(cls, rule_names: Set[str]) -> None:
        """Cek konflik kritis yang akan memunculkan exception."""
        for rule1, rule2 in cls.CRITICAL_CONFLICTS:
            if rule1 in rule_names and rule2 in rule_names:
                raise ValueError(
                    f"Critical rule conflict: '{rule1}' cannot be used with '{rule2}'"
                )

    @classmethod
    def _check_warning_conflicts(cls, rule_names: Set[str]) -> None:
        """Cek konflik fungsional yang hanya memunculkan warning."""
        for rule1, rule2 in cls.WARNING_CONFLICTS:
            if rule1 in rule_names and rule2 in rule_names:
                warnings.warn(f"Potential overlap: '{rule1}' and '{rule2}' may validate similar things", UserWarning, stacklevel=2)

    @classmethod
    def _check_parameter_conflicts(cls, rule_names: Set[str], params_map: Dict[str, List[str]]) -> None:
        """Cek konflik parameter antar rules."""
        # Range conflicts
        if 'min' in rule_names and 'max' in rule_names:
            min_val = float(params_map['min'][0])
            max_val = float(params_map['max'][0])
            if min_val > max_val:
                raise ValueError(f"Invalid range: min ({min_val}) > max ({max_val})")

        if 'between' in rule_names:
            between_vals = params_map['between']
            
            if len(between_vals) != 2:
                raise ValueError("Between rule requires exactly 2 values")
            min_val, max_val = map(float, between_vals)
            if min_val >= max_val:
                raise ValueError(f"Invalid between range: {min_val} >= {max_val}")

        # Size vs length checks
        if 'size' in rule_names and ('min' in rule_names or 'max' in rule_names):
            warnings.warn("'size' already implies exact dimension, 'min/max' may be redundant", UserWarning)

    @classmethod
    def _check_special_cases(cls, rule_names: Set[str]) -> None:
        """Cek special cases dan grup rules."""
        # Required_with/without group conflicts
        if len(cls.REQUIRED_GROUPS & rule_names) > 1:
            warnings.warn(
                "Multiple required_* conditions may cause unexpected behavior",
                UserWarning
            )

        # Prohibited_if/unless conflicts
        if len(cls.PROHIBITED_GROUPS & rule_names) > 1:
            warnings.warn(
                "Using both prohibited_if and prohibited_unless may be confusing",
                UserWarning
            )