import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from abc import ABC, abstractmethod

class DataTypeValidator(ABC):
    """Base class for all SQL data type validators"""
    
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        self.field_name = field_name
        self.data_type = data_type
        self.is_required = is_required
        self.display_name = display_name or field_name.replace('_', ' ').title()
    
    @abstractmethod
    def get_html_input_type(self) -> str:
        """Return appropriate HTML input type"""
        pass
    
    @abstractmethod
    def get_html_attributes(self) -> dict:
        """Return HTML attributes for validation"""
        pass
    
    @abstractmethod
    def validate_value(self, value: str) -> Tuple[bool, str]:
        """Validate the input value"""
        pass
    
    def get_max_length(self) -> Optional[int]:
        """Extract max length from data type like VARCHAR(30)"""
        match = re.search(r'\((\d+)\)', self.data_type)
        return int(match.group(1)) if match else None

class IntegerValidator(DataTypeValidator):
    """Validator for integer types"""
    
    INTEGER_RANGES = {
        'BIT': (0, 1),
        'TINYINT': (0, 255),
        'SMALLINT': (-32768, 32767),
        'INT': (-2147483648, 2147483647),
        'INTEGER': (-2147483648, 2147483647),
        'BIGINT': (-9223372036854775808, 9223372036854775807),
    }
    
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        super().__init__(field_name, data_type, is_required, display_name)
        self.int_type = self._get_integer_type()
        self.min_val, self.max_val = self.INTEGER_RANGES.get(self.int_type, (None, None))
        self.precision = self.get_max_length() if 'NUMERIC' in data_type.upper() else None
    
    def _get_integer_type(self) -> str:
        data_upper = self.data_type.upper()
        for int_type in self.INTEGER_RANGES.keys():
            if int_type in data_upper:
                return int_type
        if 'NUMERIC' in data_upper:
            return 'NUMERIC'
        return 'INT'
    
    def get_html_input_type(self) -> str:
        return 'number'
    
    def get_html_attributes(self) -> dict:
        attrs = {'step': '1'}  # Only whole numbers
        if self.min_val is not None:
            attrs['min'] = str(self.min_val)
        if self.max_val is not None:
            attrs['max'] = str(self.max_val)
        elif self.precision:
            # For NUMERIC(n), max is 10^n - 1
            attrs['max'] = str(10**self.precision - 1)
        return attrs
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        try:
            int_val = int(value)
        except ValueError:
            return False, f"{self.display_name} must be a whole number"
        
        # Check range
        if self.min_val is not None and int_val < self.min_val:
            return False, f"{self.display_name} must be at least {self.min_val}"
        if self.max_val is not None and int_val > self.max_val:
            return False, f"{self.display_name} must be at most {self.max_val}"
        
        # Check precision for NUMERIC
        if self.precision and len(str(abs(int_val))) > self.precision:
            return False, f"{self.display_name} must be {self.precision} digits or less"
        
        return True, ""

class DecimalValidator(DataTypeValidator):
    """Validator for decimal/float types"""
    
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        super().__init__(field_name, data_type, is_required, display_name)
        self.precision, self.scale = self._get_precision_scale()
        self.is_money = 'MONEY' in data_type.upper()
    
    def _get_precision_scale(self) -> Tuple[Optional[int], Optional[int]]:
        """Extract precision and scale from DECIMAL(10,2) format"""
        match = re.search(r'\((\d+),(\d+)\)', self.data_type)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None
    
    def get_html_input_type(self) -> str:
        return 'number'
    
    def get_html_attributes(self) -> dict:
        attrs = {}
        if self.scale:
            attrs['step'] = f"0.{'0' * (self.scale - 1)}1"
        elif self.is_money:
            attrs['step'] = '0.01'
        else:
            attrs['step'] = 'any'
        return attrs
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        try:
            float_val = float(value)
        except ValueError:
            return False, f"{self.display_name} must be a number"
        
        # Check decimal places
        if '.' in value:
            decimal_places = len(value.split('.')[1])
            if self.is_money and decimal_places > 2:
                return False, f"{self.display_name} can have at most 2 decimal places"
            elif self.scale and decimal_places > self.scale:
                return False, f"{self.display_name} can have at most {self.scale} decimal places"
        
        return True, ""

class StringValidator(DataTypeValidator):
    """Validator for string types"""
    
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        super().__init__(field_name, data_type, is_required, display_name)
        self.max_length = self.get_max_length()
        self.is_email = self._is_email_field()
    
    def _is_email_field(self) -> bool:
        return ('EMAIL' in self.field_name.upper() or 
                'EMAIL' in self.data_type.upper() or
                '@' in self.field_name.upper())
    
    def get_html_input_type(self) -> str:
        return 'email' if self.is_email else 'text'
    
    def get_html_attributes(self) -> dict:
        attrs = {}
        if self.max_length:
            attrs['maxlength'] = str(self.max_length)
        return attrs
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        if self.max_length and len(value) > self.max_length:
            return False, f"{self.display_name} must be {self.max_length} characters or less"
        
        return True, ""

class DateValidator(DataTypeValidator):
    """Validator for date-only fields"""
    
    def get_html_input_type(self) -> str:
        return 'date'
    
    def get_html_attributes(self) -> dict:
        return {}
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True, ""
        except ValueError:
            return False, f"{self.display_name} must be in YYYY-MM-DD format"

class TimeValidator(DataTypeValidator):
    """Validator for time-only fields"""
    
    def get_html_input_type(self) -> str:
        return 'time'
    
    def get_html_attributes(self) -> dict:
        return {}
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        try:
            if len(value.split(':')) == 2:
                datetime.strptime(value, '%H:%M')
            else:
                datetime.strptime(value, '%H:%M:%S')
            return True, ""
        except ValueError:
            return False, f"{self.display_name} must be in HH:MM or HH:MM:SS format"

class DateTimeValidator(DataTypeValidator):
    """Validator for datetime fields"""
    
    def get_html_input_type(self) -> str:
        return 'date'
    
    def get_html_attributes(self) -> dict:
        return {}
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        if not value.strip():
            return (not self.is_required, f"{self.display_name} is required" if self.is_required else "")
        
        formats = [
            '%Y-%m-%d',           # From date picker
            '%Y-%m-%d %H:%M:%S',  # Full datetime
            '%Y-%m-%d %H:%M',     # DateTime without seconds
            '%m/%d/%Y',           # US format
            '%m/%d/%Y %H:%M:%S',  # US with time
            '%m/%d/%Y %H:%M',     # US with time no seconds
        ]
        
        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True, ""
            except ValueError:
                continue
        
        return False, f"{self.display_name} must be a valid date/time"

def create_validator(field_name: str, data_type: str, is_required: bool, display_name: str = None) -> DataTypeValidator:
    """Factory function to create appropriate validator based on data type"""
    data_upper = data_type.upper()
    
    # Integer types
    if any(t in data_upper for t in ['BIT', 'TINYINT', 'SMALLINT', 'INT', 'INTEGER', 'BIGINT', 'NUMERIC']):
        return IntegerValidator(field_name, data_type, is_required, display_name)
    
    # Decimal types
    elif any(t in data_upper for t in ['DECIMAL', 'FLOAT', 'REAL', 'MONEY']):
        return DecimalValidator(field_name, data_type, is_required, display_name)
    
    # Time only (not datetime)
    elif 'TIME' in data_upper and 'DATETIME' not in data_upper:
        return TimeValidator(field_name, data_type, is_required, display_name)
    
    # Date only
    elif data_upper == 'DATE':
        return DateValidator(field_name, data_type, is_required, display_name)
    
    # DateTime types
    elif any(t in data_upper for t in ['DATETIME', 'SMALLDATETIME', 'DATETIME2', 'DATETIMEOFFSET', 'TIMESTAMP']):
        return DateTimeValidator(field_name, data_type, is_required, display_name)
    
    # String types (default)
    else:
        return StringValidator(field_name, data_type, is_required, display_name)

def parse_docstring(docstring: str) -> List[DataTypeValidator]:
    """
    Parse docstring with SQL field definitions using OOP validators
    Format: @FIELD_NAME DATA_TYPE IS_REQUIRED 'display_name',
    """
    fields = []
    
    # Remove extra whitespace and split by lines
    lines = [line.strip() for line in docstring.strip().split('\n') if line.strip()]
    
    for line in lines:
        # Skip empty lines and lines not starting with @
        if not line.startswith('@'):
            continue
        
        # Remove @ and trailing comma
        line = line[1:].rstrip(',').strip()
        
        # Parse with regex to handle quoted display names
        pattern = r'(\w+)\s+(\w+(?:\([0-9,]+\))?)\s+(True|False)(?:\s+[\'"]([^\'"]*)[\'"])?'
        match = re.match(pattern, line)
        
        if match:
            field_name = match.group(1)
            data_type = match.group(2)
            is_required = match.group(3).lower() == 'true'
            display_name = match.group(4) if match.group(4) else None
            
            validator = create_validator(field_name, data_type, is_required, display_name)
            fields.append(validator)
    
    return fields

def generate_output_docstring(fields: List[DataTypeValidator], form_data: Dict[str, str]) -> str:
    """Generate output docstring with filled values"""
    output_lines = ['"""']
    
    for field in fields:
        value = form_data.get(field.field_name, '')
        if value:
            # Check if the field is a string type or datetime that needs quotes
            if isinstance(field, (StringValidator, DateValidator, TimeValidator, DateTimeValidator)):
                formatted_value = f"'{value}'"
            else:
                formatted_value = value
            
            output_lines.append(f"@{field.field_name} {field.data_type} = {formatted_value},")
        else:
            output_lines.append(f"@{field.field_name} {field.data_type},")
    
    output_lines.append('"""')
    return '\n'.join(output_lines)