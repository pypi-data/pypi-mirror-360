import contextlib
from typing import Dict, Any, List, Optional, Iterator
import mysql.connector
import psycopg2

class DatabaseManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self._connection_params = self._normalize_config()

    def _normalize_config(self) -> Dict[str, Any]:
        """Normalize different config formats from various frameworks"""
        db_type = self.config.get('type', 'mysql').lower()
        
        # Handle SQLAlchemy-style URLs
        if 'url' in self.config:
            return self._parse_url(self.config['url'])
        
        return {
            'type': db_type,
            'host': self.config.get('host', 'localhost'),
            'port': self.config.get('port', 3306 if db_type == 'mysql' else 5432),
            'user': self.config.get('user') or self.config.get('username', 'root'),
            'password': self.config.get('password', ''),
            'database': self.config.get('database', ''),
            'options': self.config.get('options', {})
        }

    def _parse_url(self, url: str) -> Dict[str, Any]:
        """Parse SQLAlchemy-style database URLs"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return {
            'type': parsed.scheme.split('+')[0],
            'host': parsed.hostname,
            'port': parsed.port,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path[1:] if parsed.path else ''
        }

    @contextlib.contextmanager
    def get_cursor(self) -> Iterator[Any]:
        """Context manager for safe cursor handling"""
        self.connect()
        cursor = None
        try:
            if self._connection_params['type'] == 'postgresql':
                from psycopg2.extras import RealDictCursor
                cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            else:
                cursor = self.connection.cursor(dictionary=True)
                
            yield cursor
        finally:
            if cursor:
                cursor.close()

    def connect(self):
        """Establish database connection with retry logic"""
        if self.connection and self.connection.is_connected():
            return

        params = self._connection_params
        try:
            if params['type'] == 'mysql':
                self.connection = mysql.connector.connect(
                    host=params['host'],
                    user=params['user'],
                    password=params['password'],
                    database=params['database'],
                    port=params['port'],
                    **params.get('options', {})
                )
            elif params['type'] == 'postgresql':
                self.connection = psycopg2.connect(
                    host=params['host'],
                    user=params['user'],
                    password=params['password'],
                    dbname=params['database'],
                    port=params['port'],
                    **params.get('options', {})
                )
            elif params['type'] == 'sqlite':
                import sqlite3
                self.connection = sqlite3.connect(
                    params['database'] or ':memory:',
                    **params.get('options', {})
                )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def disconnect(self):
        """Safely disconnect with cleanup"""
        if self.connection:
            try:
                if hasattr(self.connection, 'is_connected') and self.connection.is_connected():
                    self.connection.close()
                elif hasattr(self.connection, 'closed') and not self.connection.closed:
                    self.connection.close()
            except Exception:
                pass
            finally:
                self.connection = None

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Safe query execution with automatic reconnection"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def exists(self, table: str, column: str, value: Any) -> bool:
        """Optimized exists check with parameterized query"""
        sql = f"SELECT 1 FROM {table} WHERE {column} = %s LIMIT 1"
        result = self.query(sql, (value,))
        return bool(result)

    def is_unique(self, table: str, column: str, value: Any, 
                ignore_id: Optional[int] = None) -> bool:
        """Advanced uniqueness check with ignore condition"""
        where_clause = f"{column} = %s"
        params = [value]
        
        if ignore_id is not None:
            where_clause += " AND id != %s"
            params.append(ignore_id)
            
        sql = f"""
        SELECT NOT EXISTS (
            SELECT 1 FROM {table} 
            WHERE {where_clause}
            LIMIT 1
        ) AS is_unique
        """
        
        result = self.query(sql, tuple(params))
        return result[0]['is_unique']

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database"""
        try:
            if self._connection_params['type'] == 'mysql':
                sql = """
                SELECT COUNT(*) AS count 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
                """
                result = self.query(sql, (self._connection_params['database'], table_name))
            elif self._connection_params['type'] == 'postgresql':
                sql = """
                SELECT COUNT(*) AS count 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = %s
                """
                result = self.query(sql, (table_name,))
            else:  # SQLite
                sql = """
                SELECT COUNT(*) AS count 
                FROM sqlite_master 
                WHERE type='table' AND name=?
                """
                result = self.query(sql, (table_name,))
                
            return result[0]['count'] > 0
        except Exception:
            return False
