import tkinter as tk
from table import Table
from database import connect  # Для загрузки столиков из базы данных
from tkinter import simpledialog


class RestaurantGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Restaurant Management System")
        self.root.geometry("800x600")
        self.tables = []

        # Поле для столиков
        self.canvas = tk.Canvas(self.root, bg="lightgrey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Кнопка для добавления нового столика
        add_table_button = tk.Button(self.root, text="Добавить столик", command=self.add_new_table)
        add_table_button.pack(pady=10)

        # Загрузка столиков из базы данных
        self.load_tables()

    def load_tables(self):
        """Загружаем столики из базы данных и отображаем их на экране."""
        conn = connect()
        cursor = conn.cursor()

        cursor.execute('''SELECT id, status, capacity FROM tables''')
        rows = cursor.fetchall()

        # Для каждого столика из базы создаем объект Table
        for row in rows:
            table_id, status, capacity = row
            table = Table(self.canvas, x=50, y=50, width=100, height=100,
                          table_id=table_id, status=status,
                          capacity=capacity)
            self.tables.append(table)
            table.update_table_color()  # Применяем правильный цвет к столикам при загрузке

        conn.close()

    def add_new_table(self):
        """Открываем окно для ввода параметров нового столика и добавляем его на экран."""
        capacity = simpledialog.askinteger("Новый столик", "Введите вместимость столика:", minvalue=1, maxvalue=20)

        if capacity:
            table = Table(self.canvas, x=100, y=100, width=100, height=100, table_id=None, capacity=capacity)
            self.tables.append(table)

    def run(self):
        self.root.mainloop()
