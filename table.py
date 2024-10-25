import tkinter as tk
from tkinter import ttk
from database import connect
from orders import Order  # Импортируем класс для работы с заказами
from datetime import datetime


class Table:
    def __init__(self, canvas, x, y, width, height, table_id=None, status="free", capacity=4, guests=0,
                 occupied_time=None, released_time=None):
        self.canvas = canvas
        self.table_id = table_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.status = status
        self.capacity = capacity
        self.guests = guests
        self.occupied_time = occupied_time  # Время посадки
        self.released_time = released_time  # Время освобождения

        # Создаем прямоугольник для столика
        self.rect = self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height,
                                                 fill="lightblue")

        # Обработка событий мыши
        self.canvas.tag_bind(self.rect, "<ButtonPress-1>",
                             self.on_press_left)  # Левая кнопка мыши для открытия окна управления
        self.canvas.tag_bind(self.rect, "<ButtonPress-3>",
                             self.on_press_right)  # Правая кнопка мыши для начала перетаскивания
        self.canvas.tag_bind(self.rect, "<B3-Motion>", self.on_drag_right)  # Перетаскивание с правой кнопкой мыши

    def save_to_db(self):
        """Сохраняем новый столик в базу данных."""
        conn = connect()
        cursor = conn.cursor()

        # Сохраняем столик
        cursor.execute('''INSERT INTO tables (status, capacity, guests, occupied_time, released_time)
                          VALUES (?, ?, ?, ?, ?)''',
                       (self.status, self.capacity, self.guests, self.occupied_time, self.released_time))

        self.table_id = cursor.lastrowid  # Получаем ID нового столика
        conn.commit()
        conn.close()

    def update_table_info_in_db(self):
        """Обновляем информацию столика в базе данных (статус, гости, время)."""
        conn = connect()
        cursor = conn.cursor()

        # Обновляем статус, количество гостей, время посадки и освобождения
        cursor.execute(
            '''UPDATE tables SET status = ?, guests = ?, occupied_time = ?, released_time = ? WHERE id = ?''',
            (self.status, self.guests, self.occupied_time, self.released_time, self.table_id))

        conn.commit()
        conn.close()

    def on_press_left(self, event):
        """Обрабатываем нажатие левой кнопкой мыши — открываем меню управления столиком."""
        self.manage_table()

    def manage_table(self):
        """Открываем окно для управления столиком: статус, количество человек, заказ."""
        dialog = tk.Toplevel()  # Создаем новое окно
        dialog.title(f"Управление столиком {self.table_id}")

        # Изменение статуса
        status_label = tk.Label(dialog, text="Статус столика:")
        status_label.pack(pady=5)

        status_combobox = ttk.Combobox(dialog, values=["free", "occupied", "reserved"])
        status_combobox.set(self.status)
        status_combobox.pack(pady=5)

        # Указание количества человек
        guests_label = tk.Label(dialog, text="Количество человек за столом:")
        guests_label.pack(pady=5)

        guests_entry = tk.Entry(dialog)
        guests_entry.insert(0, str(self.guests))
        guests_entry.pack(pady=5)

        # Время посадки и освобождения
        time_label = tk.Label(dialog,
                              text=f"Время посадки: {self.occupied_time or '-'}\nВремя освобождения: {self.released_time or '-'}")
        time_label.pack(pady=5)

        # Добавление заказа
        order_label = tk.Label(dialog, text="Заказ для столика:")
        order_label.pack(pady=5)

        order_text = tk.Text(dialog, height=5, width=30)
        current_order = Order.get_order_by_table(self.table_id)
        if current_order:
            order_text.insert(tk.END, current_order)
        order_text.pack(pady=5)

        # Кнопка подтверждения
        confirm_button = tk.Button(dialog, text="Сохранить",
                                   command=lambda: self.save_table_info(status_combobox.get(), guests_entry.get(),
                                                                        order_text.get("1.0", tk.END), dialog,
                                                                        time_label))
        confirm_button.pack(pady=10)

    def save_table_info(self, status, guests, order_text, dialog, time_label):
        """Сохраняем изменения статуса, количества человек, времени и заказа."""
        # Обновляем статус
        if status in ["free", "occupied", "reserved"]:
            # Если статус меняется на "occupied", записываем текущее время как время посадки
            if status == "occupied" and self.status != "occupied":
                self.occupied_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.released_time = None  # Сбрасываем время освобождения

            # Если статус меняется на "free", записываем текущее время как время освобождения
            elif status == "free" and self.status != "free":
                self.released_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.status = status
            self.update_table_color()

        # Обновляем количество гостей
        if guests.isdigit():
            self.guests = int(guests)
        self.update_table_info_in_db()  # Обновляем статус, количество гостей и время в базе данных

        # Сохраняем заказ
        if order_text.strip():
            order = Order(self.table_id)
            order.add_items(order_text.strip())
            order.save_to_db()

        # Обновляем метку времени в диалоге
        time_label.config(
            text=f"Время посадки: {self.occupied_time or '-'}\nВремя освобождения: {self.released_time or '-'}")

        dialog.destroy()

    def on_press_right(self, event):
        """Обрабатываем нажатие правой кнопкой мыши — запоминаем начальные координаты для перетаскивания."""
        self.start_x = event.x
        self.start_y = event.y

    def on_drag_right(self, event):
        """Перемещение столика при удержании правой кнопки мыши."""
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.canvas.move(self.rect, dx, dy)
        self.start_x = event.x
        self.start_y = event.y

    def update_table_color(self):
        """Изменяем цвет столика в зависимости от статуса."""
        color = "lightblue"  # По умолчанию свободный

        if self.status == "occupied":
            color = "red"
        elif self.status == "reserved":
            color = "yellow"

        # Обновляем цвет прямоугольника
        self.canvas.itemconfig(self.rect, fill=color)
