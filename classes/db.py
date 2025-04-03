import psycopg
import json

class DB_Connection:
    def __init__(self, uri, success, connection, error):
        self.uri = uri
        self.success = success
        self.connection = connection
        self.error = error
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.success = True
            self.connection = psycopg.connect(self.uri)
        except psycopg.Error as e:
            self.success = False
            self.error = e

class DB_Query:
    def __init__(self, connection, sql, success, result, error):
        self.connection = connection
        self.sql = sql
        self.success = success
        self.result = result
        self.error = error
        self.query_db()

    def query_db(self):
        data = []
        with self.connection.connection as conn:
            with conn.cursor() as cur:
                jsonQuery = "SELECT row_to_json(t) FROM (" + self.sql + ") AS t"
                try:                    
                    cur.execute(jsonQuery)                    
                    rows = cur.fetchall()

                    columns = [column[0] for column in cur.description]                    
                    for row in rows:
                        data.append(dict(zip(columns, row)))
                    self.result = json.dumps(data)

                    self.success = True
                    self.error = None
                except psycopg.Error as e:
                    self.result = None
                    self.success = False
                    self.error = e

class DB_Write:
    def __init__(self, connection, sql, success, result, error):
        self.connection = connection
        self.sql = sql
        self.success = success
        self.result = result
        self.error = error
        self.write_to_db()

    def write_to_db(self):
        with self.connection.connection as conn:
            with conn.cursor() as cur:
                jsonQuery = self.sql
                try:                    
                    cur.execute(jsonQuery) 
                    self.success = True
                    self.error = None
                except psycopg.Error as e:
                    self.result = None
                    self.success = False
                    self.error = e