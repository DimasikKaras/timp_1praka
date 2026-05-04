# main.py
from data_access import DataAccessLayer
from business_logic import BusinessLogicLayer
from presentation import PresentationLayer

if __name__ == "__main__":
    # Собираем слои, как конструктор Lego:
    # База данных не зависит ни от кого
    db_layer = DataAccessLayer()
    
    # Бизнес-логике нужна база данных
    logic_layer = BusinessLogicLayer(db_layer)
    
    # Интерфейсу нужна бизнес-логика
    ui_layer = PresentationLayer(logic_layer)
    
    # Запускаем интерфейс
    ui_layer.start()