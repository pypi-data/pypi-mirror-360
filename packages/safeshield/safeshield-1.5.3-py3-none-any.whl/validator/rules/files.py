from .base import Rule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
import mimetypes

class FileRule(Rule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        # 1. Cek file object framework (Flask/Werkzeug/FastAPI)
        if (hasattr(value, 'filename') and 
            hasattr(value, 'stream') and 
            hasattr(value, 'content_type')):
            return True
            
        # 2. Cek file-like object umum
        if hasattr(value, 'read') and callable(value.read):
            return True
            
        # 3. Cek path file yang valid (string)
        if isinstance(value, str):
            return (
                '.' in value and                  # Harus punya extension
                not value.startswith('data:') and # Bukan data URI
                not value.strip().startswith('<') # Bukan XML/HTML
            )
            
        # 4. Cek binary data langsung
        if isinstance(value, (bytes, bytearray)):
            return len(value) > 0  # Pastikan tidak kosong
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid file"

class DimensionsRule(Rule):
    def __init__(self, *params):
        super().__init__(*params)
        self._count_parameter = 1
        self._constraints = {
            'min_width': 0,
            'min_height': 0,
            'max_width': float('inf'),
            'max_height': float('inf'),
            'width': None,
            'height': None,
            'ratio': None
        }

    def maxWidth(self, value: int) -> 'DimensionsRule':
        self._constraints['width'] = None
        self._constraints['max_width'] = value
        return self

    def maxHeight(self, value: int) -> 'DimensionsRule':
        self._constraints['height'] = None
        self._constraints['max_height'] = value
        return self

    def ratio(self, value: float) -> 'DimensionsRule':
        self._constraints['ratio'] = value
        return self

    def minWidth(self, value: int) -> 'DimensionsRule':
        self._constraints['width'] = None
        self._constraints['min_width'] = value
        return self

    def minHeight(self, value: int) -> 'DimensionsRule':
        self._constraints['height'] = None
        self._constraints['min_height'] = value
        return self
    
    def _validate_constraint_logic(self):
        if self._constraints['width'] is not None:
            if (self._constraints['min_width'] > 0 or 
                self._constraints['max_width'] < float('inf')):
                raise ValueError("Cannot specify both exact width and min/max width")

        if self._constraints['max_width'] < self._constraints['min_width']:
            raise ValueError(f"max_width ({self._constraints['max_width']}) "
                f"cannot be less than min_width ({self._constraints['min_width']})")

        if self._constraints['height'] is not None:
            if (self._constraints['min_height'] > 0 or 
                self._constraints['max_height'] < float('inf')):
                raise ValueError("Cannot specify both exact height and min/max height")

        if self._constraints['max_height'] < self._constraints['min_height']:
            raise ValueError(f"max_height ({self._constraints['max_height']}) "
                f"cannot be less than min_height ({self._constraints['min_height']})")
        
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self._validate_constraint_logic()
        try:
            # 2. Parse parameters
            for param in params:
                # Format Laravel: min_width=100
                if '=' in param:
                    key, val = param.split('=', 1)
                    if key in self._constraints:
                        try:
                            self._constraints[key] = float(val)
                        except ValueError:
                            continue
                
                # Format legacy: 100x200
                elif 'x' in param:
                    try:
                        width, height = map(int, param.split('x'))
                        self._constraints['width'] = width
                        self._constraints['height'] = height
                    except ValueError:
                        continue
                
                # Format ratio: 3/2
                elif '/' in param:
                    try:
                        self._constraints['ratio'] = param
                    except ValueError:
                        continue

            # 3. Load image
            img = self._load_image(value)
            if not img:
                return False

            width, height = img.size
            actual_ratio = round(width / height, 2)

            # 4. Validate _constraints
            checks = [
                (self._constraints['width'] is None or width == self._constraints['width']),
                (self._constraints['height'] is None or height == self._constraints['height']),
                width >= self._constraints['min_width'],
                height >= self._constraints['min_height'],
                width <= self._constraints['max_width'],
                height <= self._constraints['max_height'],
                self._check_ratio(self._constraints['ratio'], actual_ratio)
            ]
            
            return all(checks)

        except Exception as e:
            print(f"Dimension validation error: {str(e)}")
            return False

    def _load_image(self, value):
        """Helper to load image from different sources"""
        try:
            from PIL import Image
            import io
            
            if hasattr(value, 'read'):  # File-like object
                value.seek(0)
                img = Image.open(value)
                value.seek(0)
                return img
            elif isinstance(value, bytes):  # Bytes
                return Image.open(io.BytesIO(value))
            elif isinstance(value, str):  # File path
                if value.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    return Image.open(value)
            return None
        except:
            return None

    def _check_ratio(self, ratio_constraint, actual_ratio):
        """Validate aspect ratio"""
        if not ratio_constraint:
            return True
            
        try:
            numerator, denominator = map(float, ratio_constraint.split('/'))
            expected_ratio = round(numerator / denominator, 2)
            return actual_ratio == expected_ratio
        except:
            return False

    def message(self, field: str, params: List[str]) -> str:
        constraints = []
        
        if self._constraints['width'] is not None:
            constraints.append(f"width={self._constraints['width']}")
        if self._constraints['height'] is not None:
            constraints.append(f"height={self._constraints['height']}")
        if self._constraints['min_width'] > 0:
            constraints.append(f"min_width={self._constraints['min_width']}")
        if self._constraints['max_width'] < float('inf'):
            constraints.append(f"max_width={self._constraints['max_width']}")
        if self._constraints['min_height'] > 0:
            constraints.append(f"min_height={self._constraints['min_height']}")
        if self._constraints['max_height'] < float('inf'):
            constraints.append(f"max_height={self._constraints['max_height']}")
        if self._constraints['ratio'] is not None:
            constraints.append(f"ratio={self._constraints['ratio']:.2f}")
        
        return f"The :attribute image must satisfy: {', '.join(constraints)}"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':width': self._constraints['width'],
            ':min_width': self._constraints['min_width'],
            ':max_width': self._constraints['max_width'],
            ':height': self._constraints['height'],
            ':min_height': self._constraints['min_height'],
            ':max_height': self._constraints['max_height'],
            ':ratio': self._constraints['ratio'],
        }
        
        return replacements
    
class ExtensionsRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        filename = (
            value.filename if hasattr(value, 'filename') 
            else str(value)
        ).lower()
        
        if '.' not in filename:
            return False
            
        ext = filename.rsplit('.', 1)[1]
        return ext in [e.lower().strip() for e in params]
    
    def message(self, field: str, params: List[str]) -> str:
        return f"File :attribute must have one of these extensions: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params)
        }
        
        return replacements
    
class ImageRule(Rule):
    VALID_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    VALID_MIME_TYPES = {
        'image/jpeg', 'image/png', 
        'image/gif', 'image/bmp', 'image/webp'
    }

    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        # Check basic file attributes
        if not hasattr(value, 'filename') and not isinstance(value, (str, bytes)):
            return False
            
        # Check extension if available
        if hasattr(value, 'filename'):
            ext = value.filename.rsplit('.', 1)[-1].lower()
            if ext not in self.VALID_EXTENSIONS:
                return False
                
        # Check MIME type if available
        if hasattr(value, 'content_type'):
            if value.content_type not in self.VALID_MIME_TYPES:
                return False
                
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be a valid image file (JPEG, PNG, GIF, BMP, or WebP)"
    
class MimeTypesRule(Rule):
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        # Check from content_type attribute
        if hasattr(value, 'content_type'):
            return value.content_type in params
            
        # Check from mimetype attribute
        if hasattr(value, 'mimetype'):
            return value.mimetype in params
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"File :attribute must be one of these types: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params)
        }
        
        return replacements
    
class MimeTypeByExtensionRule(Rule):
    _name = 'mimes'
    _count_parameter = 1
    
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if value is None or not hasattr(value, 'filename'):
            return False
            
        mimetypes.init()
        
        extension = value.filename.split('.')[-1].lower()
        
        mime_type = mimetypes.guess_type(f"file.{extension}")[0]
        
        return mime_type in params if mime_type else False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :attribute must be one of these types: :values"
    
    def replacements(self, field, value):
        replacements = {
            ':attribute': self._get_display_name(field),
            ':input': value,
            ':values': ', '.join(self._params)
        }
        
        return replacements