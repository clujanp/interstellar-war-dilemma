from sqlite3 import connect
from typing import Type
from pydantic import BaseModel
from uuid import UUID


class SQLiteRepository:
    PYTHON_TO_SQL = {
        int: "INTEGER",
        str: "TEXT",
        float: "REAL",
        bool: "BOOLEAN",
        UUID: "TEXT",
    }

    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None

    def connect(self):
        self.connection = connect(self.db_file)

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def create_table(self, table_name, columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.connection.execute(query)
        self.connection.commit()

    def insert(self, table_name, data):
        columns = ', '.join(data.keys())
        values = ', '.join(['?' for _ in data.values()])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        self.connection.execute(query, tuple(data.values()))
        self.connection.commit()

    def update(self, table_name, data, condition):
        set_values = ', '.join([f"{column} = ?" for column in data.keys()])
        query = f"UPDATE {table_name} SET {set_values} WHERE {condition}"
        self.connection.execute(query, tuple(data.values()))
        self.connection.commit()

    def delete(self, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.connection.execute(query)
        self.connection.commit()

    def select(self, table_name, condition=None):
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        cursor = self.connection.execute(query)
        rows = cursor.fetchall()
        return rows

    def build(self, models: list[Type[BaseModel]]):
        for model in models:
            table_name = model.__name__.lower()
            columns = ', '.join([
                f"{name} {self._get_sql_type(field.type_)}"
                for name, field in model.__fields__.items()
            ])
            self.create_table(table_name, columns)

    def _get_sql_type(self, python_type: Type):
        cast = self.PYTHON_TO_SQL.get(python_type, None)
        if cast is not None:
            raise ValueError(f"Unsupported type: {python_type}")
