import os
import inspect
import warnings
from typing import Dict, Any, Optional
from urllib.parse import urlparse

class DatabaseAutoDetector:
    @classmethod
    def detect(cls) -> Optional[Dict[str, Any]]:
        """Main detection method that tries all available detectors"""
        detectors = [
            cls._detect_odoo,
            cls._detect_django,
            cls._detect_flask_env,
            cls._detect_sqlalchemy,
            cls._detect_env_vars
        ]

        for detector in detectors:
            try:
                config = detector()
                if config:
                    if cls._validate_config(config):
                        return config
            except Exception as e:
                print(f"Warning: Detector {detector.__name__} failed: {str(e)}")
                continue

        print("No database configuration detected!")
        return None

    @classmethod
    def _validate_config(cls, config: Dict[str, Any]) -> bool:
        """Validate the detected configuration for all database types"""
        required_keys = ['type', 'host', 'database']
        
        # Daftar tipe database yang membutuhkan username
        requires_username = [
            'postgresql', 'mysql', 'mariadb', 'mssql', 
            'oracle', 'cockroachdb', 'redshift'
        ]
        
        # SQLite adalah kasus khusus
        if config.get('type') == 'sqlite':
            return 'database' in config
        
        # Validasi untuk database lainnya
        if not all(key in config for key in required_keys):
            return False
        
        # Periksa username untuk database yang membutuhkannya
        if config['type'] in requires_username and 'username' not in config:
            return False
            
        return True
    
    @classmethod
    def _detect_odoo(cls) -> Optional[Dict[str, Any]]:
        """Detect Odoo database configuration"""
        try:
            from odoo.tools import config
            from odoo.http import request
                
            return {
                'type': 'postgresql',
                'host': config['db_host'] or '',
                'port': str(config['db_port'] or 5432),
                'username': config['db_user'] or 'odoo',
                'password': config['db_password'] or '',
                'database': config['db_name'] or request.db,
            }
        except ImportError:
            try:
                # Cara 2: Deteksi melalui environment variables Odoo
                db_name = os.getenv('ODOO_DATABASE') or os.getenv('DB_NAME')
                if db_name:
                    return {
                        'type': 'postgresql',
                        'host': os.getenv('DB_HOST', 'localhost'),
                        'port': os.getenv('DB_PORT', '5432'),
                        'username': os.getenv('DB_USER', 'odoo'),
                        'password': os.getenv('DB_PASSWORD', ''),
                        'database': db_name
                    }
            except Exception:
                pass
        return None

    @classmethod
    def _detect_django(cls) -> Optional[Dict[str, Any]]:
        try:
            from django.conf import settings
            db = settings.DATABASES['default']
            engine = db['ENGINE'].split('.')[-1]
            
            engine_map = {
                'postgresql': 'postgresql',
                'mysql': 'mysql',
                'sqlite3': 'sqlite'
            }
            
            return {
                'type': engine_map.get(engine, engine),
                'host': db.get('HOST', 'localhost'),
                'port': db.get('PORT', '5432' if engine == 'postgresql' else '3306'),
                'username': db['USER'],
                'password': db['PASSWORD'],
                'database': db['NAME']
            }
        except ImportError:
            return None
        except Exception:  # Tangkap error spesifik Django
            return None

    @classmethod
    def _detect_sqlalchemy(cls) -> Optional[Dict[str, Any]]:
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.engine.url import make_url
            
            # Cari engine SQLAlchemy di stack frame
            for frame in inspect.stack():
                for val in frame.frame.f_locals.values():
                    if isinstance(val, type(create_engine('sqlite://'))):  # type: ignore
                        url = make_url(str(val.url))
                        return {
                            'type': url.drivername.split('+')[0],
                            'host': url.host or 'localhost',
                            'port': str(url.port) if url.port else '5432' if 'postgres' in url.drivername else '3306',
                            'username': url.username,
                            'password': url.password or '',
                            'database': url.database
                        }
            return None
        except ImportError:
            return None

    @classmethod
    def _detect_env_vars(cls) -> Optional[Dict[str, Any]]:
        from dotenv import load_dotenv
        load_dotenv()
            
        standard_vars = {
            'DB_TYPE': os.getenv('DB_TYPE'),
            'DB_HOST': os.getenv('DB_HOST'),
            'DB_USER': os.getenv('DB_USER'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD'),
            'DB_NAME': os.getenv('DB_NAME')
        }
        
        if any(standard_vars.values()):
            return {
                'type': standard_vars['DB_TYPE'] or 'mysql',
                'host': standard_vars['DB_HOST'] or 'localhost',
                'username': standard_vars['DB_USER'] or 'root',
                'password': standard_vars['DB_PASSWORD'] or '',
                'database': standard_vars['DB_NAME'] or ''
            }
        return None
    
    @classmethod
    def _detect_flask_env(cls) -> Optional[Dict[str, Any]]:
        """Deteksi konfigurasi database dari Flask app"""
        try:
            from flask import current_app
            if not current_app or not hasattr(current_app, 'config'):
                return None

            # Handle Flask-SQLAlchemy
            if 'SQLALCHEMY_DATABASE_URI' in current_app.config:
                uri = current_app.config['SQLALCHEMY_DATABASE_URI']
                return cls._parse_sqlalchemy_uri(uri)
            
            # Handle Flask default database config
            elif 'DATABASE_URL' in current_app.config:
                uri = current_app.config['DATABASE_URL']
                return cls._parse_sqlalchemy_uri(uri)
            
            # Handle Flask-MySQLdb
            elif 'MYSQL_DATABASE_HOST' in current_app.config:
                return {
                    'type': 'mysql',
                    'host': current_app.config.get('MYSQL_DATABASE_HOST', 'localhost'),
                    'port': current_app.config.get('MYSQL_DATABASE_PORT', 3306),
                    'username': current_app.config.get('MYSQL_DATABASE_USER', 'root'),
                    'password': current_app.config.get('MYSQL_DATABASE_PASSWORD', ''),
                    'database': current_app.config.get('MYSQL_DATABASE_DB', '')
                }
            return None
        except (ImportError, RuntimeError):
            return None

    @classmethod
    def _parse_sqlalchemy_uri(cls, uri: str) -> Dict[str, Any]:
        """Parse SQLAlchemy URI format"""
        from urllib.parse import urlparse
        parsed = urlparse(uri)
        
        # Mapping database types
        db_type_map = {
            'postgres': 'postgresql',
            'postgresql': 'postgresql',
            'mysql': 'mysql',
            'sqlite': 'sqlite',
            'mssql': 'mssql'
        }
        
        db_type = db_type_map.get(parsed.scheme.split('+')[0], parsed.scheme)
        
        config = {
            'type': db_type,
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or (5432 if db_type == 'postgresql' else 3306),
            'username': parsed.username or '',
            'password': parsed.password or '',
            'database': parsed.path[1:] if parsed.path else ''
        }
        
        # Handle SQLite special case
        if db_type == 'sqlite':
            config['database'] = parsed.path  # Full path termasuk leading slash
            
        return config
    
    @classmethod
    def _parse_rails_env_vars(cls) -> Optional[Dict[str, Any]]:
        """Parse Rails-style ENV variables"""
        def get_env(key, default=None):
            return os.getenv(key) or os.getenv(f'DATABASE_{key}', default)

        adapter = get_env('ADAPTER')
        if not adapter:
            return None

        # Mapping adapter Rails
        adapter_map = {
            'postgresql': 'postgresql',
            'mysql2': 'mysql',
            'sqlite3': 'sqlite'
        }

        db_type = adapter_map.get(adapter, adapter)

        return {
            'type': db_type,
            'host': get_env('HOST', 'localhost'),
            'port': int(get_env('PORT', 5432 if db_type == 'postgresql' else 3306)),
            'username': get_env('USERNAME', 'root'),
            'password': get_env('PASSWORD', ''),
            'database': get_env('DATABASE', ''),
            'timeout': int(get_env('TIMEOUT', '5000'))
        }
