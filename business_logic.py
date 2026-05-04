import hashlib
import hmac
import logging
import os
import threading

from config import HASH_SECRET, LOG_FILE


ROLE_DISPATCHER = "Диспетчер"
ROLE_EMPLOYEE = "Сотрудник"
SENSOR_TYPE_HEAT = "Тепловой"
SENSOR_TYPE_SMOKE = "Дымовой"
HEAT_THRESHOLD = 70
SMOKE_THRESHOLD = 15
PBKDF2_ITERATIONS = 600000


class AccessDeniedError(Exception):
    pass


class BusinessLogicLayer:
    def __init__(self, data_access):
        self.dal = data_access
        self.current_user = None
        self._monitor_thread = None
        self._monitor_stop_event = threading.Event()

    # --- Модуль авторизации ---
    def _hash_password(self, password, salt_bytes, iterations):
        peppered_password = f"{password}{HASH_SECRET}"
        return hashlib.pbkdf2_hmac(
            "sha256",
            peppered_password.encode(),
            salt_bytes,
            iterations,
        ).hex()

    def login(self, username, password):
        user = self.dal.get_user(username)
        if not user:
            logging.warning("Неуспешный вход: пользователь %s не найден.", username)
            return False
        salt = user.get("salt")
        stored_hash = user.get("password_hash")
        iterations = user.get("iterations", PBKDF2_ITERATIONS)
        if not salt or not stored_hash or not iterations:
            logging.error("Некорректные данные пользователя %s.", username)
            return False
        try:
            salt_bytes = bytes.fromhex(salt)
        except ValueError:
            logging.error("Некорректная соль пользователя %s.", username)
            return False
        computed_hash = self._hash_password(password, salt_bytes, iterations)
        try:
            computed_hash_bytes = bytes.fromhex(computed_hash)
            stored_hash_bytes = bytes.fromhex(stored_hash)
        except ValueError:
            logging.error("Некорректный хэш пользователя %s.", username)
            return False
        if not hmac.compare_digest(computed_hash_bytes, stored_hash_bytes):
            logging.warning("Неуспешный вход: неверный пароль для %s.", username)
            return False
        self.current_user = {"login": username, "role": user.get("role")}
        logging.info("Пользователь %s вошел в систему.", username)
        return True

    def register_user(self, username, password, role):
        if not username or not password:
            raise ValueError("Логин и пароль обязательны.")
        if role not in {ROLE_DISPATCHER, ROLE_EMPLOYEE}:
            raise ValueError("Недопустимая роль.")
        if self.dal.get_user(username):
            raise ValueError("Пользователь уже существует.")
        user_count = self.dal.get_user_count()
        if user_count > 0 and not self.current_user:
            logging.warning("Попытка регистрации без входа.")
            raise AccessDeniedError("Сначала выполните вход диспетчера.")
        if user_count > 0 and self.get_current_role() != ROLE_DISPATCHER:
            logging.warning("Отказ в доступе при регистрации.")
            raise AccessDeniedError("Регистрация доступна только диспетчеру.")
        if user_count == 0 and role != ROLE_DISPATCHER:
            raise ValueError("Первый пользователь должен быть диспетчером.")
        salt_bytes = os.urandom(16)
        salt_hex = salt_bytes.hex()
        iterations = PBKDF2_ITERATIONS
        password_hash = self._hash_password(password, salt_bytes, iterations)
        self.dal.add_user(username, password_hash, salt_hex, iterations, role)
        logging.info("Зарегистрирован пользователь %s с ролью %s.", username, role)

    def get_logs(self, limit=50):
        if self.get_current_role() != ROLE_DISPATCHER:
            user_login = self.current_user.get("login") if self.current_user else "неизвестный"
            logging.warning("Отказ в доступе к журналу для пользователя %s.", user_login)
            raise AccessDeniedError("Доступ к журналу доступен только диспетчеру.")
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as log_file:
                lines = log_file.readlines()
        except FileNotFoundError:
            return []
        return [line.rstrip("\n") for line in lines[-limit:]]

    def get_current_role(self):
        if not self.current_user:
            return None
        return self.current_user.get("role")

    # --- Анализатор показаний и менеджер прав ---
    def get_sensors_list(self):
        return self.dal.get_all_sensors()

    def get_alarms_list(self):
        return self.dal.get_alarms()

    def process_sensor_reading(self, sensor_id, new_value):
        if self.get_current_role() != ROLE_DISPATCHER:
            user_login = self.current_user.get("login") if self.current_user else "неизвестный"
            logging.warning("Отказ в доступе для пользователя %s.", user_login)
            raise AccessDeniedError("Недостаточно прав для изменения показаний.")

        sensors = self.dal.get_all_sensors()
        sensor = sensors.get(sensor_id)
        if not sensor:
            return "Датчик не найден."
        status = self._evaluate_sensor_status(sensor, new_value)
        if status == "ПОЖАР" and sensor.get("status") != "ПОЖАР":
            description = (
                f"{sensor_id} ({sensor.get('location')}): "
                f"{sensor.get('type')} датчик, значение {new_value}"
            )
            self.dal.add_alarm(sensor_id, description)
            logging.error("Пожарная тревога: %s", description)

        self.dal.update_sensor_data(sensor_id, status, new_value)
        return f"Показания обновлены. Статус: {status}"

    def _evaluate_sensor_status(self, sensor, value):
        sensor_type = sensor.get("type")
        if sensor_type == SENSOR_TYPE_HEAT and value > HEAT_THRESHOLD:
            return "ПОЖАР"
        if sensor_type == SENSOR_TYPE_SMOKE and value > SMOKE_THRESHOLD:
            return "ПОЖАР"
        return "Норма"

    # --- Мониторинг датчиков ---
    def start_monitoring(self, interval_seconds=5):
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._monitor_stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True,
        )
        self._monitor_thread.start()
        logging.info("Запущен фоновый мониторинг датчиков.")

    def stop_monitoring(self):
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_stop_event.set()
            self._monitor_thread.join(timeout=1)

    def _monitor_loop(self, interval_seconds):
        while not self._monitor_stop_event.is_set():
            self._check_sensors()
            self._monitor_stop_event.wait(interval_seconds)

    def _check_sensors(self):
        sensors = self.dal.get_all_sensors()
        for sensor_id, sensor in sensors.items():
            previous_status = sensor.get("status")
            value = (
                sensor.get("temperature")
                if sensor.get("type") == SENSOR_TYPE_HEAT
                else sensor.get("smoke_level")
            )
            if value is None:
                continue
            status = self._evaluate_sensor_status(sensor, value)
            if status != previous_status:
                self.dal.update_sensor_data(sensor_id, status, value)
            if status == "ПОЖАР" and previous_status != "ПОЖАР":
                description = (
                    f"{sensor_id} ({sensor.get('location')}): "
                    f"{sensor.get('type')} датчик, значение {value}"
                )
                self.dal.add_alarm(sensor_id, description)
                logging.error("Пожарная тревога (авто): %s", description)
