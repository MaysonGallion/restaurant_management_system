import sqlite3

DB_PATH = "db/restaurant.db"


# Функция для подключения к базе данных
def connect():
    return sqlite3.connect(DB_PATH)


# Функция для создания таблиц
def create_tables():
    conn = connect()
    cursor = conn.cursor()

    # Создание таблицы столиков
    cursor.execute('''CREATE TABLE IF NOT EXISTS tables (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        status TEXT NOT NULL,
                        capacity INTEGER NOT NULL
                      )''')

    # Создание таблицы заказов
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        table_id INTEGER,
                        items TEXT,
                        total REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (table_id) REFERENCES tables(id)
                      )''')

    # Создание таблицы сотрудников
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                      )''')

    conn.commit()  # Сохраняем изменения
    conn.close()  # Закрываем подключение
