# data_access.py

class DataAccessLayer:
    def __init__(self):
        # Эмуляция баз данных (словари и списки)
        self.users_db = {
            "admin": {"password": "123", "role": "Диспетчер"},
            "user1": {"password": "321", "role": "Сотрудник"}
        }
        self.sensors_db = {
            "S1": {"type": "Дымовой", "location": "Цех 1", "status": "Норма", "smoke_level": 0},
            "S2": {"type": "Тепловой", "location": "Склад", "status": "Норма", "temperature": 20}
        }
        self.alarms_db = [] # Журнал тревог

    # --- Методы для пользователей ---
    def get_user(self, login):
        # TODO: Вернуть пользователя по логину или None
        pass

    # --- Методы для датчиков ---
    def get_all_sensors(self):
        # TODO: Вернуть весь словарь датчиков
        pass

    def update_sensor_data(self, sensor_id, status, value):
        # TODO: Обновить статус и значение (температуру/дым) конкретного датчика
        pass

    # --- Методы для тревог ---
    def add_alarm(self, sensor_id, description):
        # TODO: Создать словарь с данными тревоги (ID, время, описание) и добавить в alarms_db
        pass

    def get_alarms(self):
        # TODO: Вернуть список всех тревог
        pass