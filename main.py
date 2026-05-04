# main.py
import logging

from business_logic import BusinessLogicLayer
from config import LOG_FILE
from data_access import DataAccessLayer
from presentation import PresentationLayer

if __name__ == "__main__":
    # Собираем слои, как конструктор Lego:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    # База данных не зависит ни от кого
    db_layer = DataAccessLayer()
    
    # Бизнес-логике нужна база данных
    logic_layer = BusinessLogicLayer(db_layer)
    
    # Интерфейсу нужна бизнес-логика
    ui_layer = PresentationLayer(logic_layer)
    
    # Запускаем фоновый мониторинг
    logic_layer.start_monitoring()

    # Запускаем интерфейс
    try:
        ui_layer.start()
    finally:
        logic_layer.stop_monitoring()
