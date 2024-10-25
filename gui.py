import tkinter as tk
from table import Table
from database import connect
from tkinter import simpledialog
from datetime import datetime


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

        # Метка для отображения текущего времени и даты
        self.time_label = tk.Label(self.root, font=('Helvetica', 12))
        self.time_label.place(x=10, y=10)  # Размещаем в левом верхнем углу
        self.update_time()  # Запускаем обновление времени

        # Загрузка столиков из базы данных
        self.load_tables()

    def update_time(self):
        """Обновляем время и дату каждую секунду."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # Обновляем каждую секунду

    def load_tables(self):
        """Загружаем столики из базы данных и отображаем их на экране."""
        conn = connect()
        cursor = conn.cursor()

        cursor.execute('''SELECT id, status, capacity FROM tables''')
        rows = cursor.fetchall()

        # Для каждого столика из базы создаем объект Table
        for row in rows:
            table_id, status, capacity = row
            table = Table(self.canvas, x=50, y=50, width=100, height=100, table_id=table_id, status=status,
                          capacity=capacity)
            self.tables.append(table)
            table.update_table_color()  # Применяем правильный цвет к столикам при загрузке

        conn.close()

    def add_new_table(self):
        """Открываем окно для ввода параметров нового столика и добавляем его на экран."""
        capacity = simpledialog.askinteger("Новый столик", "Введите вместимость столика:", minvalue=1, maxvalue=20)

        if capacity:
            # Создаем новый столик с указанной вместимостью и сохраняем его в базе данных
            table = Table(self.canvas, x=100, y=100, width=100, height=100, table_id=None, capacity=capacity)
            table.save_to_db()  # Сохраняем в базу данных, чтобы получить уникальный ID
            self.tables.append(table)

    def run(self):
        self.root.mainloop()
