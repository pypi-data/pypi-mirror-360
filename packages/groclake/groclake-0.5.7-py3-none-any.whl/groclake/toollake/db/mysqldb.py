from typing import Dict, Any, Optional, List, Union
import mysql.connector
from mysql.connector import Error

class MysqlDB:
    def __init__(self, tool_config: Dict[str, Any]):
        """
        Initialize MySQL connection with tool configuration.
        
        Expected tool_config format:
        {
            'user': 'username',
            'password': 'password',
            'host': 'hostname',
            'port': 3306,
            'database': 'database_name',
            'charset': 'utf8'
        }
        """
        self.tool_config = tool_config
        self.connection = None
        self.cursor = None
        self.database = tool_config.get('database')
        self.connect()

    def connect(self) -> None:
        """
        Establish connection to MySQL database using the tool configuration.
        """
        try:
            if self.connection and self.connection.is_connected():
                return  # Connection is active, no need to reconnect

            self.connection = mysql.connector.connect(
                user=self.tool_config.get('user'),
                password=self.tool_config.get('password'),
                host=self.tool_config.get('host'),
                port=self.tool_config.get('port', 3306),
                database=self.tool_config.get('database'),
                charset=self.tool_config.get('charset', 'utf8'),
                autocommit=True  # ensures no dangling transactions
            )
            self.cursor = self.connection.cursor(dictionary=True)

            # Set MySQL session time zone to IST
            self.cursor.execute("SET time_zone = '+05:30';")
        except Error as e:
            raise ConnectionError(f"Failed to connect to MySQL: {str(e)}")

    def ensure_connection(self) -> None:
        """
        Ensure the connection is active, reconnect if necessary.
        """
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def read(self, query: str, params: Optional[Union[tuple, dict]] = None, 
             multiple: bool = False, parsed: bool = True) -> Union[Dict, List[Dict], None]:
        """
        Execute a SELECT query and retrieve the results.

        Args:
            query (str): SQL query to execute
            params (tuple or dict, optional): Parameters for the SQL query
            multiple (bool): Whether to fetch multiple rows (True) or single row (False)
            parsed (bool): Whether to return results as dictionaries (True) or tuples (False)

        Returns:
            If multiple=True: List of dictionaries (parsed=True) or tuples (parsed=False)
            If multiple=False: Single dictionary (parsed=True) or tuple (parsed=False)
            Returns None or empty list if no results found
        """
        self.ensure_connection()
        try:
            cursor = self.connection.cursor(dictionary=parsed)
            cursor.execute(query, params)

            if multiple:
                result = cursor.fetchall()
                return result if result else []
            else:
                result = cursor.fetchone()
                return result if result else (None if not parsed else {})

        except Error as e:
            raise Exception(f"MySQL query error: {str(e)}")
        finally:
            cursor.close()
            self.connection.close()

    def write(self, query: str, params: Optional[Union[tuple, dict]] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query (str): SQL query to execute
            params (tuple or dict, optional): Parameters for the SQL query

        Returns:
            int: The last inserted ID for INSERT queries, or number of affected rows for UPDATE/DELETE
        """
        self.ensure_connection()
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            
            if query.strip().upper().startswith('INSERT'):
                return self.cursor.lastrowid
            return self.cursor.rowcount

        except Error as e:
            self.connection.rollback()
            raise Exception(f"MySQL write error: {str(e)}")

    def execute_many(self, query: str, params: List[Union[tuple, dict]]) -> int:
        """
        Execute the same query with multiple sets of parameters.

        Args:
            query (str): SQL query to execute
            params (list): List of parameter sets to execute with the query

        Returns:
            int: Number of affected rows
        """
        self.ensure_connection()
        try:
            self.cursor.executemany(query, params)
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            self.connection.rollback()
            raise Exception(f"MySQL executemany error: {str(e)}")

    def close(self) -> None:
        """
        Close the database connection and cursor.
        """
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """
        Context manager entry point.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        """
        self.close()

    def get_database(self):
        return self.database
    
    def get_database_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve the data schema (table names and columns) for the current database.

        Returns:
            dict: A dictionary with table names as keys and a list of column definitions as values.
        """
        self.ensure_connection()
        schema = {}

        try:
            query_tables = """
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = %s
            """
            self.cursor.execute(query_tables, (self.database,))
            tables = [row['table_name'] for row in self.cursor.fetchall()]

            for table in tables:
                query_columns = """
                    SELECT 
                        column_name, data_type, is_nullable, column_key, column_default, extra
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                """
                self.cursor.execute(query_columns, (self.database, table))
                columns = self.cursor.fetchall()
                schema[table] = columns

            return schema

        except Error as e:
            raise Exception(f"Failed to retrieve schema: {str(e)}")
        
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the schema (columns) of a specific table.

        Args:
            table_name (str): Name of the table to retrieve schema for.

        Returns:
            List[Dict[str, Any]]: List of dictionaries describing each column.
        """
        self.ensure_connection()
        try:
            query = """
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_KEY,
                    COLUMN_DEFAULT,
                    EXTRA,
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION,
                    NUMERIC_SCALE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """
            self.cursor.execute(query, (self.database, table_name))
            return self.cursor.fetchall()
        except Error as e:
            raise Exception(f"Error fetching schema for table '{table_name}': {str(e)}")


