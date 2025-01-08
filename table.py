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

        self.grid_size = 12  # Размер ячейки сетки
        self.resize_mode = None  # Режим изменения размеров

        # Привязка событий мыши
        # Привязка событий мыши
        self.canvas.tag_bind(self.rect, "<ButtonPress-1>", self.on_press_left)  # Левая кнопка для управления
        self.canvas.tag_bind(self.rect, "<ButtonPress-3>",
                             self.on_press_right)  # Правая кнопка для начала перетаскивания
        self.canvas.tag_bind(self.rect, "<B3-Motion>", self.on_drag_right)  # Перетаскивание правой кнопкой
        self.canvas.tag_bind(self.rect, "<ButtonRelease-3>", self.on_release_right)  # Отпускание правой кнопки
        self.canvas.tag_bind(self.rect, "<Motion>", self.on_mouse_move)  # Наведение курсора

        # События изменения размеров — только если используется средняя кнопка
        self.canvas.tag_bind(self.rect, "<ButtonPress-2>", self.start_resize)  # Средняя кнопка мыши для изменения
        self.canvas.tag_bind(self.rect, "<B2-Motion>", self.do_resize)  # Перетаскивание для изменения размеров
        self.canvas.tag_bind(self.rect, "<ButtonRelease-2>", self.stop_resize)  # Отпускание средней кнопки

    def save_to_db(self):
        """Сохраняем новый столик в базу данных или обновляем существующий."""
        conn = connect()
        cursor = conn.cursor()

        if self.table_id is None:  # Новый столик
            # Добавляем запись со всеми полями
            cursor.execute('''
                INSERT INTO tables (x, y, width, height, status, capacity, guests, released_time, occupied_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.x, self.y, self.width, self.height, self.status, self.capacity, self.guests,
                  self.released_time, self.occupied_time))

            self.table_id = cursor.lastrowid  # Получаем ID нового столика

        else:  # Обновление существующего столика
            cursor.execute('''
                UPDATE tables
                SET x = ?, y = ?, width = ?, height = ?, status = ?, capacity = ?, guests = ?, released_time = ?, occupied_time = ?
                WHERE id = ?
            ''', (self.x, self.y, self.width, self.height, self.status, self.capacity, self.guests,
                  self.released_time, self.occupied_time, self.table_id))

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

        # Перемещаем прямоугольник
        self.canvas.move(self.rect, dx, dy)

        # Обновляем стартовые координаты
        self.start_x = event.x
        self.start_y = event.y

    def update_table_color(self):
        """Изменяем цвет столика в зависимости от статуса."""
        if self.status == "free":
            color = "lightblue"
        elif self.status == "occupied":
            color = "red"
        elif self.status == "reserved":
            color = "yellow"
        else:
            color = "gray"  # По умолчанию свободный

        # Обновляем цвет прямоугольника
        self.canvas.itemconfig(self.rect, fill=color)

    def snap_to_grid(self):
        """Привязываем столик к ближайшей ячейке сетки"""
        grid_size = 12  # Размер ячейки сетки (100x100 пикселей)

        # Вычисляем ближайшие координаты для привязки
        snapped_x = round(self.x / grid_size) * grid_size
        snapped_y = round(self.y / grid_size) * grid_size

        # обновляем кооординаты столика
        self.x = snapped_x
        self.y = snapped_y

        self.canvas.coords(self.rect, self.x, self.y, self.x + self.width, self.y + self.height)

    def on_release_right(self, event):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)

        self.x = x1
        self.y = y1

        self.snap_to_grid()
        self.update_table_info_in_db()

    def start_resize(self, event):
        """Начало изменения размеров столика."""
        self.resize_mode = self.get_resize_mode(event.x, event.y)

    def do_resize(self, event):
        """Изменение размеров столика в зависимости от режима."""
        if not self.resize_mode:
            return

        # Логика изменения размеров
        if "right" in self.resize_mode:
            self.width = max(self.grid_size, self.align_to_grid(event.x - self.x))
        if "bottom" in self.resize_mode:
            self.height = max(self.grid_size, self.align_to_grid(event.y - self.y))
        if "left" in self.resize_mode:
            new_width = max(self.grid_size, self.align_to_grid(self.width + (self.x - event.x)))
            self.x += self.width - new_width
            self.width = new_width
        if "top" in self.resize_mode:
            new_height = max(self.grid_size, self.align_to_grid(self.height + (self.y - event.y)))
            self.y += self.height - new_height
            self.height = new_height

        # Обновляем координаты прямоугольника
        self.canvas.coords(self.rect, self.x, self.y, self.x + self.width, self.y + self.height)

    def stop_resize(self, event):
        """Завершаем изменение размеров столика."""
        self.resize_mode = None
        self.update_table_info_in_db()

    def align_to_grid(self, value):
        """Выравнивает значение (ширину или высоту) по сетке."""
        return round(value / self.grid_size) * self.grid_size

    def get_resize_mode(self, mouse_x, mouse_y):
        """Определяем, какой угол или грань столика изменяется."""
        margin = 8  # Расширяем чувствительную область

        # Проверяем углы
        if abs(mouse_x - self.x) < margin and abs(mouse_y - self.y) < margin:
            return "top_left"
        if abs(mouse_x - (self.x + self.width)) < margin and abs(mouse_y - self.y) < margin:
            return "top_right"
        if abs(mouse_x - self.x) < margin and abs(mouse_y - (self.y + self.height)) < margin:
            return "bottom_left"
        if abs(mouse_x - (self.x + self.width)) < margin and abs(mouse_y - (self.y + self.height)) < margin:
            return "bottom_right"

        # Проверяем грани
        if abs(mouse_x - self.x) < margin:
            return "left"
        if abs(mouse_x - (self.x + self.width)) < margin:
            return "right"
        if abs(mouse_y - self.y) < margin:
            return "top"
        if abs(mouse_y - (self.y + self.height)) < margin:
            return "bottom"

        return None

    def on_mouse_move(self, event):
        """Меняем курсор мыши в зависимости от положения на столике."""
        mode = self.get_resize_mode(event.x, event.y)
        if mode in ["top", "bottom"]:
            self.canvas.config(cursor="sb_v_double_arrow")  # Вертикальная стрелка
        elif mode in ["left", "right"]:
            self.canvas.config(cursor="sb_h_double_arrow")  # Горизонтальная стрелка
        elif mode in ["top_left", "bottom_right"]:
            self.canvas.config(cursor="size_nw_se")  # Диагональная стрелка ↘
        elif mode in ["top_right", "bottom_left"]:
            self.canvas.config(cursor="size_ne_sw")  # Диагональная стрелка ↙
        else:
            self.canvas.config(cursor="arrow")  # Стандартный курсор
