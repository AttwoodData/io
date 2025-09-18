import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class FieldDefinition:
    def __init__(self, field_name: str, data_type: str, is_required: bool, display_name: str = None):
        self.field_name = field_name
        self.data_type = data_type.upper()
        self.is_required = is_required
        self.display_name = display_name or field_name.replace('_', ' ').title()
        
    def get_html_input_type(self) -> str:
        """Convert SQL data type to appropriate HTML input type"""
        if 'INT' in self.data_type or 'DECIMAL' in self.data_type or 'FLOAT' in self.data_type:
            return 'number'
        elif 'DATETIME' in self.data_type or 'DATE' in self.data_type:
            return 'datetime-local' if 'DATETIME' in self.data_type else 'date'
        elif 'EMAIL' in self.data_type:
            return 'email'
        else:
            return 'text'
    
    def get_max_length(self) -> Optional[int]:
        """Extract max length from VARCHAR(n) or similar"""
        match = re.search(r'\((\d+)\)', self.data_type)
        return int(match.group(1)) if match else None
    
    def validate_value(self, value: str) -> Tuple[bool, str]:
        """Validate input value against field definition"""
        if not value.strip():
            if self.is_required:
                return False, f"{self.display_name} is required"
            return True, ""
        
        # Check string length
        max_length = self.get_max_length()
        if max_length and len(value) > max_length:
            return False, f"{self.display_name} must be {max_length} characters or less"
        
        # Check numeric types
        if 'INT' in self.data_type:
            try:
                int(value)
            except ValueError:
                return False, f"{self.display_name} must be a whole number"
        
        elif 'DECIMAL' in self.data_type or 'FLOAT' in self.data_type:
            try:
                float(value)
            except ValueError:
                return False, f"{self.display_name} must be a number"
        
        # Check date formats
        elif 'DATETIME' in self.data_type:
            try:
                datetime.fromisoformat(value.replace('T', ' '))
            except ValueError:
                return False, f"{self.display_name} must be in YYYY-MM-DD HH:MM format"
        
        elif 'DATE' in self.data_type:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return False, f"{self.display_name} must be in YYYY-MM-DD format"
        
        return True, ""

def parse_docstring(docstring: str) -> List[FieldDefinition]:
    """
    Parse docstring with SQL field definitions
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
        
        # Parse with regex to handle quoted display names and complex data types like DECIMAL(10,2)
        pattern = r'(\w+)\s+(\w+(?:\([0-9,]+\))?)\s+(True|False)(?:\s+[\'"]([^\'"]*)[\'"])?'
        match = re.match(pattern, line)
        
        if match:
            field_name = match.group(1)
            data_type = match.group(2)
            is_required = match.group(3).lower() == 'true'
            display_name = match.group(4) if match.group(4) else None
            
            fields.append(FieldDefinition(field_name, data_type, is_required, display_name))
    
    return fields

def generate_output_docstring(fields: List[FieldDefinition], form_data: Dict[str, str]) -> str:
    """Generate output docstring with filled values"""
    output_lines = ['"""']
    
    for field in fields:
        value = form_data.get(field.field_name, '')
        if value:
            output_lines.append(f"@{field.field_name} {field.data_type} = {value},")
        else:
            output_lines.append(f"@{field.field_name} {field.data_type},")
    
    output_lines.append('"""')
    return '\n'.join(output_lines)