import tkinter as tk
from table import Table


class RestaurantGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Restaurant Management System")
        self.root.geometry("800x600")
        self.tables = []

        self.canvas = tk.Canvas(self.root, bg="lightgrey")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.add_sample_tables()

    def add_sample_tables(self):
        table1 = Table(self.canvas, x=50, y=50, width=100, height=100, table_id=1)
        table2 = Table(self.canvas, x=200, y=50, width=150, height=100, table_id=2)
        self.tables.extend([table1, table2])

    def run(self):
        self.root.mainloop()

