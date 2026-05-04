# presentation.py

class PresentationLayer:
    def __init__(self, business_logic):
        self.bll = business_logic # Ссылка на бизнес-логику

    def start(self):
        # TODO: Сделать бесконечный цикл (while True).
        # Спрашивать логин и пароль. Передавать их в self.bll.login(...)
        # Если успешно - вызывать self.main_menu()
        pass

    def main_menu(self):
        # TODO: Показать меню:
        # 1. Список датчиков
        # 2. Журнал тревог
        # 3. Изменить показания датчика (Эмуляция)
        # 0. Выход
        
        # TODO: В зависимости от выбора пользователя, вызывать нужные методы (show_sensors, show_alarms и т.д.)
        pass

    def show_sensors(self):
        # TODO: Получить список от self.bll.get_sensors_list() и красиво вывести через print
        pass

    def show_alarms(self):
        # TODO: Получить список от self.bll.get_alarms_list() и красиво вывести
        pass

    def simulate_reading(self):
        # TODO: Спросить у пользователя ID датчика и новое значение (число).
        # Передать это в self.bll.process_sensor_reading(...)
        # Распечатать ответ (Успешно или Ошибка прав доступа/превышение)
        pass