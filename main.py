from gui import RestaurantGUI
from database import create_tables
from auth import AuthWindow


def main():
    create_tables()

    # def on_login_success():
    app = RestaurantGUI()  # Создаем экземпляр класса RestaurantGUI
    app.run()  # Вызываем метод run

    # auth = AuthWindow(on_login_success)
    # auth.run()


if __name__ == "__main__":
    main()
