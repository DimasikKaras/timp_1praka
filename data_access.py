# data_access.py
import hashlib
import os
from datetime import datetime

DEFAULT_PBKDF2_ITERATIONS = 600_000

class DataAccessLayer:
    def __init__(self):
        # Эмуляция баз данных (словари и списки)
        self.users_db = {}
        self._add_user("admin", "Admin#2024", "Диспетчер")
        self._add_user("user1", "User1#2024", "Сотрудник")
        self.sensors_db = {
            "S1": {"type": "Дымовой", "location": "Цех 1", "status": "Норма", "smoke_level": 0},
            "S2": {"type": "Тепловой", "location": "Склад", "status": "Норма", "temperature": 20}
        }
        self.alarms_db = [] # Журнал тревог

    def _add_user(self, login, password, role):
        salt = os.urandom(16).hex()
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            DEFAULT_PBKDF2_ITERATIONS,
        ).hex()
        self.users_db[login] = {
            "password_hash": password_hash,
            "salt": salt,
            "iterations": DEFAULT_PBKDF2_ITERATIONS,
            "role": role,
        }

    # --- Методы для пользователей ---
    def get_user(self, login):
        # TODO: Вернуть пользователя по логину или None
        return self.users_db.get(login)

    # --- Методы для датчиков ---
    def get_all_sensors(self):
        # TODO: Вернуть весь словарь датчиков
        return self.sensors_db

    def update_sensor_data(self, sensor_id, status, value):
        # TODO: Обновить статус и значение (температуру/дым) конкретного датчика
        sensor = self.sensors_db.get(sensor_id)
        if not sensor:
            return False
        sensor["status"] = status
        if sensor.get("type") == "Дымовой":
            sensor["smoke_level"] = value
        elif sensor.get("type") == "Тепловой":
            sensor["temperature"] = value
        return True

    # --- Методы для тревог ---
    def add_alarm(self, sensor_id, description):
        # TODO: Создать словарь с данными тревоги (ID, время, описание) и добавить в alarms_db
        alarm = {
            "sensor_id": sensor_id,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "description": description,
        }
        self.alarms_db.append(alarm)
        return alarm

    def get_alarms(self):
        # TODO: Вернуть список всех тревог
        return self.alarms_db
