# data_access.py
from datetime import datetime

class DataAccessLayer:
    def __init__(self):
        # Эмуляция баз данных (словари и списки)
        self.users_db = {
            "admin": {
                "password_hash": (
                    "99ddc676ef185aff1d8edb972b70aa4886d4b7763fc2bc65c19eba7f9b4c2c12"
                ),
                "salt": "admin_salt",
                "role": "Диспетчер",
            },
            "user1": {
                "password_hash": (
                    "9fe30c29a826557ae10938708864bfa889c567b5e5063df5dd71ce569469d027"
                ),
                "salt": "user1_salt",
                "role": "Сотрудник",
            },
        }
        self.sensors_db = {
            "S1": {"type": "Дымовой", "location": "Цех 1", "status": "Норма", "smoke_level": 0},
            "S2": {"type": "Тепловой", "location": "Склад", "status": "Норма", "temperature": 20}
        }
        self.alarms_db = [] # Журнал тревог

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
