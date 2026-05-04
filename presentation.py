# presentation.py
import getpass

class PresentationLayer:
    def __init__(self, business_logic):
        self.bll = business_logic # Ссылка на бизнес-логику

    def start(self):
        # TODO: Сделать бесконечный цикл (while True).
        # Спрашивать логин и пароль. Передавать их в self.bll.login(...)
        # Если успешно - вызывать self.main_menu()
        while True:
            username = input("Логин: ").strip()
            password = getpass.getpass("Пароль: ").strip()
            if self.bll.login(username, password):
                print("Вход выполнен.")
                should_exit = self.main_menu()
                if should_exit:
                    print("Выход из программы.")
                    return
            else:
                print("Неверный логин или пароль.")

    def main_menu(self):
        # TODO: Показать меню:
        # 1. Список датчиков
        # 2. Журнал тревог
        # 3. Изменить показания датчика (Эмуляция)
        # 0. Выход
        
        # TODO: В зависимости от выбора пользователя, вызывать нужные методы (show_sensors, show_alarms и т.д.)
        while True:
            print("\nМеню:")
            print("1. Список датчиков")
            print("2. Журнал тревог")
            print("3. Изменить показания датчика (Эмуляция)")
            print("0. Выход")
            choice = input("Выберите пункт: ").strip()
            if choice == "1":
                self.show_sensors()
            elif choice == "2":
                self.show_alarms()
            elif choice == "3":
                self.simulate_reading()
            elif choice == "0":
                return True
            else:
                print("Неверный выбор. Попробуйте снова.")

    def show_sensors(self):
        # TODO: Получить список от self.bll.get_sensors_list() и красиво вывести через print
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
        # TODO: Получить список от self.bll.get_alarms_list() и красиво вывести
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

    def simulate_reading(self):
        # TODO: Спросить у пользователя ID датчика и новое значение (число).
        # Передать это в self.bll.process_sensor_reading(...)
        # Распечатать ответ (Успешно или Ошибка прав доступа/превышение)
        sensor_id = input("Введите ID датчика: ").strip()
        raw_value = input("Введите новое значение: ").strip()
        try:
            new_value = float(raw_value)
        except ValueError:
            print("Некорректное значение. Пожалуйста, введите число.")
            return
        result = self.bll.process_sensor_reading(sensor_id, new_value)
        print(result)
