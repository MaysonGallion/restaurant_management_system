import tkinter as tk
from table import Table
from database import connect
from tkinter import simpledialog
from datetime import datetime


class RestaurantGUI:
    def __init__(self):
        # Настройка главного окна
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

        # Размер ячейки сетки
        self.grid_size = 12

        # Рисуем сетку
        self.draw_grid()

        # Панель управления
        control_panel = tk.Frame(self.root, bg="white", height=0)
        control_panel.pack(fill=tk.X, side=tk.BOTTOM)

        # Кнопка для добавления столика
        add_table_button = tk.Button(self.root, text="Добавить столик", command=self.add_new_table)
        add_table_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Метка времени
        self.time_label = tk.Label(self.root, font=('Helvetica', 12))
        self.time_label.pack(side=tk.RIGHT, padx=10)

        self.update_time()  # Обновление времени

        # Загружаем столики после рисования сетки
        self.load_tables()  # Загружаем столики после настройки интерфейса

    def load_tables(self):
        """Загружаем столики из базы данных и отображаем их на холсте."""
        conn = connect()  # Подключаемся к базе данных
        cursor = conn.cursor()

        # Получаем данные всех столиков из базы
        cursor.execute('SELECT id, x, y, width, height, status, capacity, guests FROM tables')
        rows = cursor.fetchall()

        for row in rows:
            # Извлекаем параметры столика
            table_id, x, y, width, height, status, capacity, guests = row

            # Нормализуем статус
            status = status.strip().lower() if status else "free"

            # Создаем объект Table
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

            # Обновляем цвет столика
            table.update_table_color()

            # Устанавливаем правильный порядок слоев
            self.canvas.tag_raise(table.rect)  # Поднимаем столик над сеткой

            # Добавляем столик в список
            self.tables.append(table)

        conn.close()  # Закрываем соединение

    def on_canvas_resize(self, event):
        """Перерисовываем сетку при изменении размера окна."""
        self.draw_grid()

    def draw_grid(self):
        """Рисуем сетку на холсте."""
        # Удаляем предыдущие линии сетки
        self.canvas.delete("grid_line")

        # Получаем размеры холста
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Рисуем вертикальные линии
        for x in range(0, width, self.grid_size):
            self.canvas.create_line(x, 0, x, height, fill="gray", dash=(2, 4), tags="grid_line")

        # Рисуем горизонтальные линии
        for y in range(0, height, self.grid_size):
            self.canvas.create_line(0, y, width, y, fill="gray", dash=(2, 4), tags="grid_line")

        # Убедимся, что сетка находится "ниже" всех столиков
        self.canvas.tag_lower("grid_line")

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
