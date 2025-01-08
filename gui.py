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

        # Создаём верхнюю панель (меню)

        self.create_menu()

        # Поле для столиков
        self.canvas = tk.Canvas(self.root, bg="lightgrey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Привязываем событие изменения размера окна
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Рисуем сетку
        self.grid_size = 12  # Размер ячейки сетки
        self.draw_grid()

        # Панель управления (включает кнопку "Добавить столик" и время)
        control_panel = tk.Frame(self.root, bg="white", height=0)
        control_panel.pack(fill=tk.X, side=tk.BOTTOM)

        # Кнопка для добавления нового столика
        add_table_button = tk.Button(self.root, text="Добавить столик", command=self.add_new_table)
        add_table_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Метка для отображения текущего времени и даты
        self.time_label = tk.Label(self.root, font=('Helvetica', 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)  # Размещаем в левом верхнем углу

        self.update_time()  # Запускаем обновление времени

        # Загрузка столиков из базы данных
        self.load_tables()

    def on_canvas_resize(self, event):
        """Перерисовываем сетку при изменении размера окна."""
        self.draw_grid()

    def draw_grid(self):
        """Рисуем сетку на поле для столиков."""
        self.canvas.delete("grid_line")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Вертикальные линии
        for x in range(0, width, self.grid_size):
            self.canvas.create_line(x, 0, x, height, fill="gray", dash=(2, 4))

        # Горизонтальные линии
        for y in range(0, height, self.grid_size):
            self.canvas.create_line(0, y, width, y, fill="gray", dash=(2, 4))

    def create_menu(self):
        """Создаём верхнюю панель с меню."""
        menubar = tk.Menu(self.root)

        # Меню "Настройки"
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Add a new user", command=self.add_user)

        menubar.add_cascade(label="Settings", menu=settings_menu)
        self.root.config(menu=menubar)

    def update_time(self):
        """Обновляем время и дату каждую секунду."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)  # Обновляем каждую секунду

    def load_tables(self):
        """Загружаем столики из базы данных и отображаем их на экране."""
        conn = connect()
        cursor = conn.cursor()

        # Загружаем все столики из базы данных
        cursor.execute('SELECT id, x, y, width, height, status, capacity, guests FROM tables')
        rows = cursor.fetchall()

        for row in rows:
            table_id, x, y, width, height, status, capacity, guests = row

            # Создаём объект столика
            table = Table(
                self.canvas,
                x=x,
                y=y,
                width=width,
                height=height,
                table_id=table_id,
                status=status,
                capacity=capacity,
                guests=guests
            )

            # Устанавливаем цвет в зависимости от статуса
            table.update_table_color()

            # Добавляем столик в список
            self.tables.append(table)

        conn.close()

    def add_new_table(self):
        """Добавляем новый столик с минимальными данными и сохраняем его в базу."""
        capacity = simpledialog.askinteger("Новый столик", "Введите вместимость столика:", minvalue=1, maxvalue=20)

        if capacity:
            # Создаём новый объект столика
            table = Table(
                self.canvas,
                x=100,  # Стартовые координаты
                y=100,
                width=50,  # Стандартные размеры
                height=50,
                table_id=None,  # Новый столик
                status="free",  # Статус по умолчанию
                capacity=capacity,
                guests=0,  # Гостей нет
                occupied_time=None,  # Время посадки отсутствует
                released_time=None  # Время освобождения отсутствует
            )

            # Сохраняем столик в базу данных
            table.save_to_db()

            # Добавляем столик в список
            self.tables.append(table)

    def add_user(self):
        pass

    def run(self):
        self.root.mainloop()
