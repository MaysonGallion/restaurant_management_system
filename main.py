from gui import RestaurantGUI
from database import create_tables


def main():
    create_tables()
    app = RestaurantGUI()  # Создаем экземпляр класса RestaurantGUI
    app.run()  # Вызываем метод run


if __name__ == "__main__":
    main()
