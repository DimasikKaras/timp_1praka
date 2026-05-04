# business_logic.py
import hashlib
import hmac

from data_access import DEFAULT_PBKDF2_ITERATIONS

ROLE_DISPATCHER = "Диспетчер"
SENSOR_TYPE_HEAT = "Тепловой"
SENSOR_TYPE_SMOKE = "Дымовой"
HEAT_THRESHOLD = 70
SMOKE_THRESHOLD = 15

class BusinessLogicLayer:
    def __init__(self, data_access):
        self.dal = data_access # Ссылка на слой данных
        self.current_user = None # Кто сейчас авторизован

    # --- Модуль авторизации ---
    def login(self, username, password):
        # TODO: Получить юзера из self.dal. Проверить пароль. 
        # Если ок -> сохранить в self.current_user и вернуть True. Иначе False.
        user = self.dal.get_user(username)
        if not user:
            return False
        salt = user.get("salt")
        stored_hash = user.get("password_hash")
        iterations = user.get("iterations", DEFAULT_PBKDF2_ITERATIONS)
        if not salt or not stored_hash or not iterations:
            return False
        try:
            salt_bytes = bytes.fromhex(salt)
        except ValueError:
            return False
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt_bytes,
            iterations,
        ).hex()
        try:
            computed_hash_bytes = bytes.fromhex(computed_hash)
            stored_hash_bytes = bytes.fromhex(stored_hash)
        except ValueError:
            return False
        if not hmac.compare_digest(computed_hash_bytes, stored_hash_bytes):
            return False
        self.current_user = {"login": username, "role": user.get("role")}
        return True

    def get_current_role(self):
        # TODO: Вернуть роль текущего пользователя
        if not self.current_user:
            return None
        return self.current_user.get("role")

    # --- Анализатор показаний и менеджер прав ---
    def get_sensors_list(self):
        # TODO: Просто запросить список у self.dal и вернуть его
        return self.dal.get_all_sensors()

    def get_alarms_list(self):
        # TODO: Запросить список тревог у self.dal
        return self.dal.get_alarms()

    def process_sensor_reading(self, sensor_id, new_value):
        # TODO: ПРОВЕРКА ПРАВ! Разрешить менять показания только "Диспетчеру".
        # Если прав нет, вернуть ошибку.
        if self.get_current_role() != ROLE_DISPATCHER:
            return "Ошибка прав доступа."
        
        # TODO: ЛОГИКА АНАЛИЗА! 
        # Запросить тип датчика у self.dal. 
        # Если тепловой и new_value > 70 -> статус "ПОЖАР".
        # Если дымовой и new_value > 15 -> статус "ПОЖАР".
        # Иначе -> статус "Норма".
        sensors = self.dal.get_all_sensors()
        sensor = sensors.get(sensor_id)
        if not sensor:
            return "Датчик не найден."
        sensor_type = sensor.get("type")
        status = "Норма"
        if sensor_type == SENSOR_TYPE_HEAT and new_value > HEAT_THRESHOLD:
            status = "ПОЖАР"
        elif sensor_type == SENSOR_TYPE_SMOKE and new_value > SMOKE_THRESHOLD:
            status = "ПОЖАР"
        
        # TODO: Если статус стал "ПОЖАР", вызвать self.dal.add_alarm(...)
        if status == "ПОЖАР":
            description = (
                f"{sensor_id} ({sensor.get('location')}): "
                f"{sensor_type} датчик, значение {new_value}"
            )
            self.dal.add_alarm(sensor_id, description)
        
        # TODO: Сохранить новые данные через self.dal.update_sensor_data(...)
        self.dal.update_sensor_data(sensor_id, status, new_value)
        return f"Показания обновлены. Статус: {status}"
