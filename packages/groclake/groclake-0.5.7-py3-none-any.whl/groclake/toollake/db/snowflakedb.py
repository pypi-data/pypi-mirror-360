import snowflake.connector
from typing import Dict, Any

class SnowflakeDB():
    def __init__(self, tool_config: Dict[str, Any]):
        self.tool_config = tool_config
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.connection = snowflake.connector.connect(
                user=self.tool_config.get('user'),
                password=self.tool_config.get('password'),
                account=self.tool_config.get('account'),
                warehouse=self.tool_config.get('warehouse'),
                database=self.tool_config.get('database'),
                schema=self.tool_config.get('schema')
            )
            self.cursor = self.connection.cursor()
        except snowflake.connector.Error as e:
            print(f"Error connecting to Snowflake: {e}")
            self.connection = None

    def read(self, query, params=None):
        self.ensure_connection()
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except snowflake.connector.Error as e:
            raise Exception(f"Snowflake query error: {e}")

    def write(self, query, params=None):
        self.ensure_connection()
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except snowflake.connector.Error as e:
            self.connection.rollback()
            raise Exception(f"Error executing write query: {e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None

    def ensure_connection(self):
        if not self.connection:
            self.connect()