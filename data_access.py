import psycopg2
from psycopg2.extras import RealDictCursor

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


class DataAccessLayer:
    def __init__(self):
        self.connection_params = {
            "host": DB_HOST,
            "port": DB_PORT,
            "dbname": DB_NAME,
            "user": DB_USER,
            "password": DB_PASSWORD,
        }
        self._ensure_schema()

    def connect(self):
        return psycopg2.connect(**self.connection_params)

    def execute_query(self, query, params=None, fetchone=False, fetchall=False, commit=False):
        conn = self.connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                result = None
                if fetchone:
                    result = cursor.fetchone()
                elif fetchall:
                    result = cursor.fetchall()
            if commit:
                conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_schema(self):
        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                iterations INTEGER NOT NULL,
                role TEXT NOT NULL
            )
            """,
            commit=True,
        )
        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS sensors (
                sensor_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL,
                smoke_level DOUBLE PRECISION,
                temperature DOUBLE PRECISION
            )
            """,
            commit=True,
        )
        self.execute_query(
            """
            CREATE TABLE IF NOT EXISTS alarms (
                id SERIAL PRIMARY KEY,
                sensor_id TEXT REFERENCES sensors(sensor_id),
                created_at TIMESTAMP NOT NULL,
                description TEXT NOT NULL
            )
            """,
            commit=True,
        )
        if not self.has_sensors():
            self.execute_query(
                """
                INSERT INTO sensors (sensor_id, type, location, status, smoke_level, temperature)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                ("S1", "Дымовой", "Цех 1", "Норма", 0, None),
                commit=True,
            )
            self.execute_query(
                """
                INSERT INTO sensors (sensor_id, type, location, status, smoke_level, temperature)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                ("S2", "Тепловой", "Склад", "Норма", None, 20),
                commit=True,
            )

    # --- Методы для пользователей ---
    def get_user(self, login):
        return self.execute_query(
            "SELECT username, password_hash, salt, iterations, role FROM users WHERE username = %s",
            (login,),
            fetchone=True,
        )

    def add_user(self, login, password_hash, salt, iterations, role):
        self.execute_query(
            """
            INSERT INTO users (username, password_hash, salt, iterations, role)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (login, password_hash, salt, iterations, role),
            commit=True,
        )

    def get_user_count(self):
        row = self.execute_query(
            "SELECT COUNT(*) AS count FROM users",
            fetchone=True,
        )
        return row["count"] if row else 0

    # --- Методы для датчиков ---
    def get_all_sensors(self):
        rows = self.execute_query(
            """
            SELECT sensor_id, type, location, status, smoke_level, temperature
            FROM sensors
            """,
            fetchall=True,
        )
        sensors = {}
        for row in rows or []:
            sensors[row["sensor_id"]] = {
                "type": row["type"],
                "location": row["location"],
                "status": row["status"],
                "smoke_level": row["smoke_level"],
                "temperature": row["temperature"],
            }
        return sensors

    def get_sensor_count(self):
        row = self.execute_query(
            "SELECT COUNT(*) AS count FROM sensors",
            fetchone=True,
        )
        return row["count"] if row else 0

    def update_sensor_data(self, sensor_id, status, value):
        sensor = self.execute_query(
            "SELECT type FROM sensors WHERE sensor_id = %s",
            (sensor_id,),
            fetchone=True,
        )
        if not sensor:
            return False
        sensor_type = sensor["type"]
        if sensor_type == "Дымовой":
            self.execute_query(
                """
                UPDATE sensors
                SET status = %s, smoke_level = %s
                WHERE sensor_id = %s
                """,
                (status, value, sensor_id),
                commit=True,
            )
        else:
            self.execute_query(
                """
                UPDATE sensors
                SET status = %s, temperature = %s
                WHERE sensor_id = %s
                """,
                (status, value, sensor_id),
                commit=True,
            )
        return True

    # --- Методы для тревог ---
    def add_alarm(self, sensor_id, description):
        row = self.execute_query(
            """
            INSERT INTO alarms (sensor_id, created_at, description)
            VALUES (%s, NOW(), %s)
            RETURNING sensor_id, created_at, description
            """,
            (sensor_id, description),
            fetchone=True,
            commit=True,
        )
        if not row:
            return None
        return {
            "sensor_id": row["sensor_id"],
            "time": row["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "description": row["description"],
        }

    def get_alarms(self):
        rows = self.execute_query(
            """
            SELECT sensor_id, created_at, description
            FROM alarms
            ORDER BY created_at DESC
            """,
            fetchall=True,
        )
        alarms = []
        for row in rows or []:
            alarms.append(
                {
                    "sensor_id": row["sensor_id"],
                    "time": row["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                    "description": row["description"],
                }
            )
        return alarms

    def has_sensors(self):
        row = self.execute_query(
            "SELECT 1 FROM sensors LIMIT 1",
            fetchone=True,
        )
        return row is not None
