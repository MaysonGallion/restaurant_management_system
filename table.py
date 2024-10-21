class Table:
    def __init__(self, canvas, x, y, width, height, table_id):
        self.canvas = canvas
        self.table_id = table_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.rect = self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height,
                                                 fill="lightblue")
        self.canvas.tag_bind(self.rect, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rect, "<B1-Motion>", self.on_drag)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.canvas.move(self.rect, dx, dy)
        self.start_x = event.x
        self.start_y = event.y
