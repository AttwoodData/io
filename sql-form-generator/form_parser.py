"""
Simplified Three-Class Validation System for SQL Form Generator
================================================================

This module provides a clean, mathematical approach to form validation using three base classes:
- NumericValidator: Handles all number types (integers, decimals, currency)
- StringValidator: Handles all text types with optional email validation  
- DateTimeValidator: Handles dates, times, and datetimes with smart defaults
"""

import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union
from abc import ABC, abstractmethod


class BaseValidator(ABC):
    """Abstract base class for all SQL data type validators"""
    
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        """
        Initialize validator with field metadata
        
        Args:
            field_name: SQL field name (e.g., 'USER_ID')
            data_type: SQL data type (e.g., 'VARCHAR(50)', 'INT', 'DATETIME')
            is_required: Whether field is required (True/False)
            display_name: Human-readable name for forms (optional)
        """
        self.field_name = field_name
        self.data_type = data_type.upper()
        self.is_required = is_required
        self.display_name = display_name or self._generate_display_name()
    
    def _generate_display_name(self) -> str:
        """Convert field_name to human-readable format"""
        return self.field_name.replace('_', ' ').title()
    
    @abstractmethod
    def get_html_input_type(self) -> str:
        """Return appropriate HTML input type (e.g., 'number', 'text', 'date')"""
        pass
    
    @abstractmethod
    def get_html_attributes(self) -> Dict[str, str]:
        """Return dictionary of HTML attributes for validation"""
        pass
    
    @abstractmethod
    def validate_value(self, value: str) -> Tuple[bool, str]:
        """
        Validate input value against field constraints
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        pass
    
    def _extract_size_params(self) -> Tuple[Optional[int], Optional[int]]:
        """
        Extract size parameters from data type
        
        Returns:
            (precision, scale) where:
            - VARCHAR(50) → (50, None)
            - DECIMAL(10,2) → (10, 2)
            - INT → (None, None)
        """
        # Match patterns like (10), (10,2)
        match = re.search(r'\((\d+)(?:,(\d+))?\)', self.data_type)
        if match:
            precision = int(match.group(1))
            scale = int(match.group(2)) if match.group(2) else None
            return precision, scale
        return None, None


class NumericValidator(BaseValidator):
    """
    Unified validator for all numeric types using mathematical properties
    
    Numeric types are defined by:
    - min_value: Minimum allowed value
    - max_value: Maximum allowed value  
    - decimal_places: Number of decimal places (0 = integer)
    - is_currency: Special formatting for money types
    """
    
    # T-SQL numeric type specifications
    TYPE_SPECS = {
        'BIT': {'min': 0, 'max': 1, 'decimals': 0},
        'TINYINT': {'min': 0, 'max': 255, 'decimals': 0},
        'SMALLINT': {'min': -32768, 'max': 32767, 'decimals': 0},
        'INT': {'min': -2147483648, 'max': 2147483647, 'decimals': 0},
        'INTEGER': {'min': -2147483648, 'max': 2147483647, 'decimals': 0},
        'BIGINT': {'min': -9223372036854775808, 'max': 9223372036854775807, 'decimals': 0},
        'FLOAT': {'min': None, 'max': None, 'decimals': None},  # Variable precision
        'REAL': {'min': None, 'max': None, 'decimals': None},   # Variable precision
        'MONEY': {'min': None, 'max': None, 'decimals': 2, 'currency': True},
        'SMALLMONEY': {'min': None, 'max': None, 'decimals': 2, 'currency': True},
    }
    
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        super().__init__(field_name, data_type, is_required, display_name)
        
        # Determine numeric properties
        self.min_value, self.max_value, self.decimal_places = self._determine_numeric_properties()
        self.is_integer = (self.decimal_places == 0)
        self.is_currency = self._is_currency_type()
    
    def _determine_numeric_properties(self) -> Tuple[Optional[int], Optional[int], int]:
        """Determine min, max, and decimal places from data type"""
        
        # Find base type
        base_type = self._get_base_type()
        spec = self.TYPE_SPECS.get(base_type, {})
        
        # Handle NUMERIC and DECIMAL with custom precision/scale
        if base_type in ['NUMERIC', 'DECIMAL']:
            precision, scale = self._extract_size_params()
            if precision:
                max_val = (10 ** (precision - (scale or 0))) - 1
                return -max_val, max_val, scale or 0
            return None, None, 0
        
        return spec.get('min'), spec.get('max'), spec.get('decimals', 0)
    
    def _get_base_type(self) -> str:
        """Extract base type from data type string"""
        for type_name in self.TYPE_SPECS.keys():
            if type_name in self.data_type:
                return type_name
        
        # Check for NUMERIC/DECIMAL
        if any(t in self.data_type for t in ['NUMERIC', 'DECIMAL']):
            return 'NUMERIC'
        
        return 'INT'  # Default fallback
    
    def _is_currency_type(self) -> bool:
        """Check if this is a currency/money type"""
        return 'MONEY' in self.data_type
    
    def get_html_input_type(self) -> str:
        """Return appropriate HTML input type based on numeric properties"""
        # Boolean detection: min=0, max=1, integer type
        if self.min_value == 0 and self.max_value == 1 and self.is_integer:
            return 'checkbox'
        
        # All other numeric types use number input
        return 'number'
    
    def get_html_attributes(self) -> Dict[str, str]:
        """Generate HTML5 validation attributes"""
        attrs = {}
        
        # Boolean/checkbox fields need different attributes
        if self.min_value == 0 and self.max_value == 1 and self.is_integer:
            # Checkbox attributes
            attrs['value'] = '1'  # When checked, value is 1
            return attrs
        
        # Numeric fields get min/max/step attributes
        if self.min_value is not None:
            attrs['min'] = str(self.min_value)
        if self.max_value is not None:
            attrs['max'] = str(self.max_value)
        
        # Set step for decimal precision
        if self.is_integer:
            attrs['step'] = '1'  # Only whole numbers
        elif self.decimal_places:
            attrs['step'] = f"0.{'0' * (self.decimal_places - 1)}1"  # e.g., "0.01" for 2 decimals
        else:
            attrs['step'] = 'any'  # Allow any decimal precision
        
        return attrs
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        """Validate numeric value against constraints"""
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        # Parse as integer or float
        try:
            if self.is_integer:
                numeric_value = int(value)
                # Reject values with decimals for integer types
                if '.' in value:
                    return False, f"{self.display_name} must be a whole number"
            else:
                numeric_value = float(value)
        except ValueError:
            return False, f"{self.display_name} must be a valid number"
        
        # Check range constraints
        if self.min_value is not None and numeric_value < self.min_value:
            return False, f"{self.display_name} must be at least {self.min_value}"
        if self.max_value is not None and numeric_value > self.max_value:
            return False, f"{self.display_name} must be at most {self.max_value}"
        
        # Check decimal places for currency and decimal types
        if self.decimal_places is not None and '.' in value:
            actual_decimals = len(value.split('.')[1])
            if actual_decimals > self.decimal_places:
                return False, f"{self.display_name} can have at most {self.decimal_places} decimal places"
        
        return True, ""


class StringValidator(BaseValidator):
    """
    Validator for all text-based types with optional email validation
    
    String types are defined by:
    - max_length: Maximum character length
    - min_length: Minimum character length (optional)
    - is_email: Whether to apply email validation
    """
    
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        super().__init__(field_name, data_type, is_required, display_name)
        
        # Extract length constraints
        precision, _ = self._extract_size_params()
        self.max_length = precision
        self.min_length = None  # Could be extended for specific requirements
        
        # Determine if this should be treated as an email field
        self.is_email = self._detect_email_field()
    
    def _detect_email_field(self) -> bool:
        """
        Detect if field should use email validation
        
        Checks field name and data type for email indicators
        """
        email_indicators = ['EMAIL', 'MAIL', '@']
        return any(indicator in self.field_name.upper() or indicator in self.data_type 
                  for indicator in email_indicators)
    
    def get_html_input_type(self) -> str:
        """Use email input for email fields, text for others"""
        return 'email' if self.is_email else 'text'
    
    def get_html_attributes(self) -> Dict[str, str]:
        """Generate HTML5 validation attributes"""
        attrs = {}
        
        # Set length constraints
        if self.max_length:
            attrs['maxlength'] = str(self.max_length)
        if self.min_length:
            attrs['minlength'] = str(self.min_length)
        
        # Add email pattern for additional validation
        if self.is_email:
            attrs['pattern'] = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
            attrs['title'] = 'Please enter a valid email address'
        
        return attrs
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        """Validate string value against constraints"""
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        # Check length constraints
        if self.min_length and len(value) < self.min_length:
            return False, f"{self.display_name} must be at least {self.min_length} characters"
        if self.max_length and len(value) > self.max_length:
            return False, f"{self.display_name} must be {self.max_length} characters or less"
        
        # Email validation
        if self.is_email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                return False, f"{self.display_name} must be a valid email address"
        
        return True, ""


class DateTimeValidator(BaseValidator):
    """
    Simplified validator for all date/time types
    
    Relies on HTML input types for validation:
    - DATE fields → HTML date picker (calendar)
    - TIME fields → HTML time picker (clock)
    - DATETIME fields → HTML date picker (time defaults to 00:00:00 in output)
    """
    
    # All legacy T-SQL date/time type names
    DATE_TYPES = ['DATE']
    TIME_TYPES = ['TIME']
    DATETIME_TYPES = ['DATETIME', 'DATETIME2', 'SMALLDATETIME', 'TIMESTAMP', 'DATETIMEOFFSET']
    
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        super().__init__(field_name, data_type, is_required, display_name)
        
        # Determine date/time category
        self.datetime_category = self._get_datetime_category()
    
    def _get_datetime_category(self) -> str:
        """
        Categorize into DATE, TIME, or DATETIME based on data type
        
        Returns:
            'DATE', 'TIME', or 'DATETIME'
        """
        # Check for TIME types (but not DATETIME variants)
        if any(t in self.data_type for t in self.TIME_TYPES) and not any(dt in self.data_type for dt in self.DATETIME_TYPES):
            return 'TIME'
        
        # Check for pure DATE types
        if any(t in self.data_type for t in self.DATE_TYPES) and not any(dt in self.data_type for dt in self.DATETIME_TYPES):
            return 'DATE'
        
        # Everything else is DATETIME
        return 'DATETIME'
    
    def get_html_input_type(self) -> str:
        """Return HTML input type - let browser handle validation"""
        if self.datetime_category == 'TIME':
            return 'time'    # Clock picker
        elif self.datetime_category == 'DATE':
            return 'date'    # Calendar picker
        else:
            return 'date'    # Calendar picker for datetime (time defaults)
    
    def get_html_attributes(self) -> Dict[str, str]:
        """Let HTML5 handle validation - minimal attributes needed"""
        return {}
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        """Minimal validation - HTML inputs provide properly formatted values"""
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        # HTML date/time inputs provide valid formats, so just check if value exists
        return True, ""
    
    def format_for_output(self, value: str) -> str:
        """
        Format value for SQL output string
        
        - DATE: Use as-is (YYYY-MM-DD)
        - TIME: Use as-is (HH:MM:SS or HH:MM)
        - DATETIME: Add 00:00:00 if only date provided
        """
        if not value:
            return value
        
        # For datetime fields, if only date provided (YYYY-MM-DD), add default time
        if self.datetime_category == 'DATETIME' and len(value) == 10:
            return f"{value} 00:00:00"
        
        return value


def create_validator(field_name: str, data_type: str, is_required: bool, display_name: str = None) -> BaseValidator:
    """
    Factory function to create appropriate validator based on data type
    
    Args:
        field_name: SQL field name
        data_type: SQL data type string
        is_required: Whether field is required
        display_name: Optional display name for forms
        
    Returns:
        Appropriate validator instance
    """
    data_upper = data_type.upper()
    
    # Numeric types (integers, decimals, currency)
    numeric_types = ['BIT', 'TINYINT', 'SMALLINT', 'INT', 'INTEGER', 'BIGINT', 
                     'NUMERIC', 'DECIMAL', 'FLOAT', 'REAL', 'MONEY', 'SMALLMONEY']
    if any(num_type in data_upper for num_type in numeric_types):
        return NumericValidator(field_name, data_type, is_required, display_name)
    
    # Date/Time types
    datetime_types = ['DATE', 'TIME', 'DATETIME', 'SMALLDATETIME', 'DATETIME2', 
                      'TIMESTAMP', 'DATETIMEOFFSET']
    if any(dt_type in data_upper for dt_type in datetime_types):
        return DateTimeValidator(field_name, data_type, is_required, display_name)
    
    # String types (default - everything else)
    return StringValidator(field_name, data_type, is_required, display_name)


def parse_docstring(docstring: str) -> List[BaseValidator]:
    """
    Parse SQL field definitions from docstring format
    
    Expected format:
    @FIELD_NAME DATA_TYPE IS_REQUIRED 'Optional Display Name'
    
    Example:
    '''
    @USER_ID INT True 'User ID'
    @EMAIL_ADDRESS VARCHAR(100) True 'Email Address'
    @BIRTH_DATE DATE False 'Date of Birth'
    '''
    
    Args:
        docstring: Multi-line string with field definitions
        
    Returns:
        List of validator instances
    """
    validators = []
    
    # Split into lines and clean
    lines = [line.strip() for line in docstring.strip().split('\n') if line.strip()]
    
    for line in lines:
        # Skip lines that don't start with @
        if not line.startswith('@'):
            continue
        
        # Remove @ and trailing comma
        line = line[1:].rstrip(',').strip()
        
        # Parse with regex: FIELD_NAME DATA_TYPE REQUIRED 'DISPLAY_NAME'
        pattern = r'(\w+)\s+(\w+(?:\([0-9,]+\))?)\s+(True|False)(?:\s+[\'"]([^\'"]*)[\'"])?'
        match = re.match(pattern, line)
        
        if match:
            field_name = match.group(1)
            data_type = match.group(2)
            is_required = match.group(3).lower() == 'true'
            display_name = match.group(4) if match.group(4) else None
            
            validator = create_validator(field_name, data_type, is_required, display_name)
            validators.append(validator)
    
    return validators


def generate_output_docstring(validators: List[BaseValidator], form_data: Dict[str, str]) -> str:
    """
    Generate SQL output docstring with form values
    
    Args:
        validators: List of field validators
        form_data: Dictionary of form field values
        
    Returns:
        Formatted SQL docstring with values
    """
    output_lines = ['"""']
    
    for validator in validators:
        value = form_data.get(validator.field_name, '')
        
        if value:
            # Format value based on validator type
            if isinstance(validator, NumericValidator):
                # Numbers are unquoted
                formatted_value = value
            elif isinstance(validator, DateTimeValidator):
                # Handle datetime formatting and quote
                if validator.is_datetime:
                    formatted_value = f"'{validator.format_for_output(value)}'"
                else:
                    formatted_value = f"'{value}'"
            else:
                # Strings are quoted
                formatted_value = f"'{value}'"
            
            output_lines.append(f"@{validator.field_name} {validator.data_type} = {formatted_value},")
        else:
            # Empty fields show just the field definition
            output_lines.append(f"@{validator.field_name} {validator.data_type},")
    
    output_lines.append('"""')
    return '\n'.join(output_lines)