# business_logic.py

class BusinessLogicLayer:
    def __init__(self, data_access):
        self.dal = data_access # Ссылка на слой данных
        self.current_user = None # Кто сейчас авторизован

    # --- Модуль авторизации ---
    def login(self, username, password):
        # TODO: Получить юзера из self.dal. Проверить пароль. 
        # Если ок -> сохранить в self.current_user и вернуть True. Иначе False.
        pass

    def get_current_role(self):
        # TODO: Вернуть роль текущего пользователя
        pass

    # --- Анализатор показаний и менеджер прав ---
    def get_sensors_list(self):
        # TODO: Просто запросить список у self.dal и вернуть его
        pass

    def get_alarms_list(self):
        # TODO: Запросить список тревог у self.dal
        pass

    def process_sensor_reading(self, sensor_id, new_value):
        # TODO: ПРОВЕРКА ПРАВ! Разрешить менять показания только "Диспетчеру".
        # Если прав нет, вернуть ошибку.
        
        # TODO: ЛОГИКА АНАЛИЗА! 
        # Запросить тип датчика у self.dal. 
        # Если тепловой и new_value > 70 -> статус "ПОЖАР".
        # Если дымовой и new_value > 15 -> статус "ПОЖАР".
        # Иначе -> статус "Норма".
        
        # TODO: Если статус стал "ПОЖАР", вызвать self.dal.add_alarm(...)
        
        # TODO: Сохранить новые данные через self.dal.update_sensor_data(...)
        pass