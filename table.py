import tkinter as tk
from tkinter import ttk
from database import connect


class Table:
    def __init__(self, canvas, x, y, width, height, table_id=None, status="free", capacity=4):
        self.canvas = canvas
        self.table_id = table_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.status = status
        self.capacity = capacity

        # Создаем прямоугольник для столика
        self.rect = self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height,
                                                 fill="lightblue")

        # Обработка событий мыши
        self.canvas.tag_bind(self.rect, "<ButtonPress-1>",
                             self.on_press_left)  # Левая кнопка мыши для изменения статуса
        self.canvas.tag_bind(self.rect, "<ButtonPress-3>",
                             self.on_press_right)  # Правая кнопка мыши для начала перетаскивания
        self.canvas.tag_bind(self.rect, "<B3-Motion>", self.on_drag_right)  # Перетаскивание с правой кнопкой мыши

    def save_to_db(self):
        """Сохраняем новый столик в базу данных."""
        conn = connect()
        cursor = conn.cursor()

        # Сохраняем столик
        cursor.execute('''INSERT INTO tables (status, capacity)
                          VALUES (?, ?)''', (self.status, self.capacity))

        self.table_id = cursor.lastrowid  # Получаем ID нового столика
        conn.commit()
        conn.close()

    def update_status_in_db(self):
        """Обновляем статус столика в базе данных."""
        conn = connect()
        cursor = conn.cursor()

        # Обновляем статус столика в базе данных
        cursor.execute('''UPDATE tables SET status = ? WHERE id = ?''', (self.status, self.table_id))

        conn.commit()
        conn.close()

    def on_press_left(self, event):
        """Обрабатываем нажатие левой кнопкой мыши — открываем окно для изменения статуса."""
        print(f"Столик с ID {self.table_id} был нажат левой кнопкой")  # Для отладки
        self.change_status()

    def on_press_right(self, event):
        """Обрабатываем нажатие правой кнопкой мыши — запоминаем начальные координаты для перетаскивания."""
        print(f"Начало перетаскивания столика с ID {self.table_id} правой кнопкой")  # Для отладки
        self.start_x = event.x
        self.start_y = event.y

    def on_drag_right(self, event):
        """Перемещение столика при удержании правой кнопки мыши."""
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.canvas.move(self.rect, dx, dy)
        self.start_x = event.x
        self.start_y = event.y
        print(f"Столик с ID {self.table_id} перемещен на ({dx}, {dy})")  # Для отладки

    def change_status(self):
        """Открываем окно для изменения статуса столика с выпадающим списком."""
        dialog = tk.Toplevel()  # Создаем новое окно
        dialog.title("Изменить статус столика")

        label = tk.Label(dialog, text="Выберите статус столика:")
        label.pack(pady=10)

        # Выпадающий список для выбора статуса
        status_combobox = ttk.Combobox(dialog, values=["free", "occupied", "reserved"])
        status_combobox.set(self.status)  # Устанавливаем текущий статус по умолчанию
        status_combobox.pack(pady=10)

        # Кнопка подтверждения
        confirm_button = tk.Button(dialog, text="Подтвердить",
                                   command=lambda: self.set_status(status_combobox.get(), dialog))
        confirm_button.pack(pady=10)

        dialog.geometry("+500+400")  # Позиционируем окно для наглядности

    def set_status(self, new_status, dialog):
        """Устанавливаем новый статус и закрываем диалоговое окно."""
        if new_status in ["free", "occupied", "reserved"]:
            print(f"Статус столика обновлен на: {new_status}")  # Для отладки
            self.status = new_status
            self.update_status_in_db()  # Обновляем статус в базе данных
            self.update_table_color()  # Обновляем цвет столика

        dialog.destroy()  # Закрываем диалоговое окно

    def update_table_color(self):
        """Изменяем цвет столика в зависимости от статуса."""
        color = "lightblue"  # По умолчанию свободный

        if self.status == "occupied":
            color = "red"
        elif self.status == "reserved":
            color = "yellow"

        # Обновляем цвет прямоугольника
        self.canvas.itemconfig(self.rect, fill=color)
