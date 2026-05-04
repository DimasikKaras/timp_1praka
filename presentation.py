import getpass

from business_logic import AccessDeniedError, ROLE_DISPATCHER, ROLE_EMPLOYEE


class PresentationLayer:
    def __init__(self, business_logic):
        self.bll = business_logic

    def start(self):
        while True:
            print("\nДобро пожаловать!")
            print("1. Вход")
            print("2. Регистрация")
            print("0. Выход")
            choice = input("Выберите пункт: ").strip()
            if choice == "1":
                if self._login_flow():
                    should_exit = self.main_menu()
                    if should_exit:
                        print("Выход из программы.")
                        return
            elif choice == "2":
                self.register_user()
            elif choice == "0":
                print("Выход из программы.")
                return
            else:
                print("Неверный выбор. Попробуйте снова.")

    def _login_flow(self):
        username = input("Логин: ").strip()
        password = getpass.getpass("Пароль: ").strip()
        if self.bll.login(username, password):
            print("Вход выполнен.")
            return True
        print("Неверный логин или пароль.")
        return False

    def main_menu(self):
        while True:
            print("\nМеню:")
            print("1. Список датчиков")
            print("2. Журнал тревог")
            print("3. Изменить показания датчика (Эмуляция)")
            print("4. Регистрация")
            print("5. Журнал событий")
            print("0. Выход")
            choice = input("Выберите пункт: ").strip()
            if choice == "1":
                self.show_sensors()
            elif choice == "2":
                self.show_alarms()
            elif choice == "3":
                self.simulate_reading()
            elif choice == "4":
                self.register_user()
            elif choice == "5":
                self.show_logs()
            elif choice == "0":
                return True
            else:
                print("Неверный выбор. Попробуйте снова.")

    def register_user(self):
        print("\nРегистрация пользователя")
        username = input("Новый логин: ").strip()
        password = getpass.getpass("Новый пароль: ").strip()
        print("Роль:")
        print("1. Диспетчер")
        print("2. Сотрудник")
        role_choice = input("Выберите роль: ").strip()
        if role_choice == "1":
            role = ROLE_DISPATCHER
        elif role_choice == "2":
            role = ROLE_EMPLOYEE
        else:
            print("Неверная роль.")
            return
        try:
            self.bll.register_user(username, password, role)
        except AccessDeniedError as exc:
            print(f"Ошибка прав доступа: {exc}")
            return
        except ValueError as exc:
            print(f"Ошибка регистрации: {exc}")
            return
        print("Пользователь успешно зарегистрирован.")

    def show_sensors(self):
        sensors = self.bll.get_sensors_list()
        if not sensors:
            print("Датчики отсутствуют.")
            return
        print("\nСписок датчиков:")
        for sensor_id, data in sensors.items():
            sensor_type = data.get("type")
            if sensor_type == "Дымовой":
                value_label = "Дым"
                value = data.get("smoke_level")
            else:
                value_label = "Температура"
                value = data.get("temperature")
            print(
                f"{sensor_id}: {sensor_type} | {data.get('location')} | "
                f"{data.get('status')} | {value_label}: {value}"
            )

    def show_alarms(self):
        alarms = self.bll.get_alarms_list()
        if not alarms:
            print("Тревог нет.")
            return
        print("\nЖурнал тревог:")
        for index, alarm in enumerate(alarms, start=1):
            print(
                f"{index}. {alarm.get('time')} | "
                f"{alarm.get('sensor_id')} | {alarm.get('description')}"
            )

    def show_logs(self):
        logs = self.bll.get_logs()
        if not logs:
            print("Записей в журнале нет.")
            return
        print("\nЖурнал событий:")
        for line in logs:
            print(line)

    def simulate_reading(self):
        sensor_id = input("Введите ID датчика: ").strip()
        raw_value = input("Введите новое значение (число, можно с дробной частью): ").strip()
        try:
            new_value = float(raw_value)
        except ValueError:
            print("Некорректное значение. Введите число, допускается дробная часть.")
            return
        try:
            result = self.bll.process_sensor_reading(sensor_id, new_value)
        except AccessDeniedError as exc:
            print(f"Ошибка прав доступа: {exc}")
            return
        print(result)
