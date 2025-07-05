"""
    Author: Jpastor
    Version: 1.0.0
    License: MIT License
    Date: 2025-07-04
"""

"""This module provides runtime support for type hints"""
from typing import Any

import mysql.connector
from mysql.connector.errors import Error

class Connector:
    """
    Class to manage the connection to the MySQL database.
    """

    def __init__(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "proyecto123",
        database: str = "apartamentos",
    ):
        """Constructor for the Connector class.

        Args:
            host (str): _description_. Defaults to 'localhost'.
            user (str): _description_. Defaults to 'root'.
            password (str): _description_. Defaults to 'proyecto123'.
            database (str): _description_. Defaults to 'apartamentos'.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.table: str | None = None

    def connect(self):
        """Establish a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            if self.connection.is_connected():
                print("✅ Conexión exitosa")
        except Error as e:
            print(f"❌ Error al conectar: {e}")

    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Conexión cerrada")

    def set_table(self, table: str):
        """Set the table to be used for database operations.

        Args:
            table (str): table name to set for operations.
        """
        self.table = table

    def insert(self, fields: list[str], values: tuple[Any, ...]) -> int:
        """Insert a new record into the table.

        Args:
            fields (list[str]): _list of field names to insert into_
            values (tuple[Any, ...]): _tuple of values to insert into the fields_

        Returns:
            _type_: integer
        """
        placeholders = ", ".join(["%s"] * len(fields))
        fields_str = ", ".join(fields)
        sql = f"INSERT INTO {self.table} ({fields_str}) VALUES ({placeholders})"
        return self._execute(sql, values)

    def update(
        self, fields: list[str], values: tuple[Any, ...], id_field: str, id_value: Any
    ) -> int:
        """Update an existing record in the table.

        Args:
            fields (list[str]): _list of field names to update_
            values (tuple[Any, ...]): _tuple of values to update the fields with_
            id_field (str): _field name to identify the record to update_
            id_value (Any): _value to identify the record to update_

        Returns:
            _type_: integer
        """
        set_clause = ", ".join([f"{field}=%s" for field in fields])
        sql = f"UPDATE {self.table} SET {set_clause} WHERE {id_field}=%s"
        return self._execute(sql, values + (id_value,))

    def get_all(self) -> list[Any]:
        """Get all records from the table.

        Returns:
            list[Any]: list of all records in the table
        """
        sql = f"SELECT * FROM {self.table}"
        return self._fetch(sql)

    def get_filtered(self, where_clause: str) -> list[Any]:
        """Get records from the table that match a specific condition.

        Args:
            where_clause (str): SQL WHERE clause to filter records.

        Returns:
            list[Any]: list of records that match the condition
        """
        sql = f"SELECT * FROM {self.table} WHERE {where_clause}"
        return self._fetch(sql)

    def _execute(self, sql: str, params: tuple[Any, ...] | None = None) -> int:
        """ Execute a SQL command that modifies the database (INSERT, UPDATE, DELETE).

        Args:
            sql (str): SQL command to execute.
            params (tuple[Any, ...] | None, optional): Parameters to bind to the SQL command. Defaults to None.

        Returns:
            int: Number of affected rows, or 0 if the execution failed.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connect()
            if self.connection is None:
                print("❌ No se pudo establecer la conexión a la base de datos.")
                return 0
            cursor = self.connection.cursor()
            cursor.execute(sql, params or ())
            self.connection.commit()
            affected = cursor.rowcount
            cursor.close()
            print(f"✅ Ejecutado: {sql}")
            return affected
        except Error as e:
            print(f"❌ Error ejecutando: {e}")
            return 0

    def _fetch(self, sql: str) -> list[Any]:
        """ Fetch records from the database based on a SQL query.

        Args:
            sql (str): SQL query to execute.

        Returns:
            list[Any]: List of records fetched from the database, or an empty list if an error occurs.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connect()
            if self.connection is None:
                print("❌ No se pudo establecer la conexión a la base de datos.")
                return []
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"❌ Error al consultar: {e}")
            return []
