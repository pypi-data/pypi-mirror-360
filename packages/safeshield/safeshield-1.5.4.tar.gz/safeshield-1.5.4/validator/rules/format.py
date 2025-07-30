from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
import re
import ipaddress
import json
import uuid
import dns.resolver
import idna

# =============================================
# FORMAT VALIDATION RULES
# =============================================

class EmailRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        """
        Available params:
        - rfc: RFCValidation (default)
        - strict: NoRFCWarningsValidation
        - dns: DNSCheckValidation
        - spoof: SpoofCheckValidation
        - filter: FilterEmailValidation
        - filter_unicode: FilterEmailValidation::unicode()
        """
        
        if not isinstance(value, str):
            return False

        # Default to RFC validation if no params specified
        validation_types = params if params else ['rfc']

        # Apply all requested validations
        for validation in validation_types:
            if validation == 'rfc' and not self._validate_rfc(value):
                return False
            elif validation == 'strict' and not self._validate_strict(value):
                return False
            elif validation == 'dns' and not self._validate_dns(value):
                return False
            elif validation == 'spoof' and not self._validate_spoof(value):
                return False
            elif validation == 'filter' and not self._validate_filter(value):
                return False
            elif validation == 'filter_unicode' and not self._validate_filter_unicode(value):
                return False

        return True

    def _validate_rfc(self, email: str) -> bool:
        """Strict RFC-compliant email validation (single-line version)"""
        return bool(re.match(
            r"^(?!(\.|\.\.))[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@(?=.{1,255}$)[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$", 
            email
        ))

    def _validate_strict(self, email: str) -> bool:
        """Strict RFC validation (no warnings)"""
        if not self._validate_rfc(email):
            return False
        
        # No leading/trailing dots
        if email.startswith('.') or email.endswith('.'):
            return False
            
        # No consecutive dots
        if '..' in email.split('@')[0]:
            return False
            
        return True

    def _validate_dns(self, email: str) -> bool:
        """DNS MX record validation"""
        try:
            domain = email.split('@')[-1]
            return bool(dns.resolver.resolve(domain, 'MX'))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, 
            dns.resolver.NoNameservers, dns.exception.DNSException):
            return False

    def _validate_spoof(self, email: str) -> bool:
        """Spoof/homograph detection"""
        try:
            domain_part = email.split('@')[-1]
            ascii_domain = idna.encode(domain_part).decode('ascii')
            
            # Check for homographs
            if domain_part != ascii_domain:
                return False
                
            # Check for deceptive characters
            return not any(ord(char) > 127 for char in email)
        except idna.IDNAError:
            return False

    def _validate_filter(self, email: str) -> bool:
        """PHP filter_var compatible validation"""
        return bool(re.match(
            r"^(?!(\.|\.\.))[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$",
            email
        ))

    def _validate_filter_unicode(self, email: str) -> bool:
        """PHP filter_var with Unicode support"""
        return bool(re.match(
            r"^(?!(\.|\.\.))[\w.!#$%&'*+/=?^_`{|}~-]+@[\w-]+(?:\.[\w-]+)*$",
            email,
            re.UNICODE
        ))

    def message(self, field: str, params: List[str]) -> str:
        base_msg = "The :attribute must be a valid email address"
        
        if 'strict' in params:
            base_msg += " (strict RFC compliance)"
        if 'dns' in params:
            base_msg += " with valid DNS records"
        if 'spoof' in params:
            base_msg += " without spoofed characters"
        if 'filter' in params:
            base_msg += " (PHP filter compatible)"
        if 'filter_unicode' in params:
            base_msg += " (Unicode allowed)"
            
        return f"{base_msg}."
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params if self._params else ['rfc']),
        }
        
        return replacements

class UrlRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(
            r'^(https?:\/\/)?'  # protocol
            r'([\da-z\.-]+)\.'  # domain
            r'([a-z\.]{2,6})'   # top level domain
            r'([\/\w \.-]*)*\/?$',  # path/query
            value
        ))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid URL."

class JsonRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid JSON string."

class UuidRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid UUID."

class UlidRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(r'^[0-9A-HJKMNP-TV-Z]{26}$', value))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid ULID."

class IpRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid IP address."

class HexRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(r'^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', value))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid hexadecimal color code."
