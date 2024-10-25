from database import connect


class Order:
    def __init__(self, table_id):
        self.table_id = table_id
        self.items = []
        self.total = 0.0  # Значение по умолчанию для total

    def add_items(self, item):
        """Добавляем блюдо в заказ."""
        self.items.append(item)

    def save_to_db(self):
        """Сохраняем заказ в базу данных."""
        conn = connect()
        cursor = conn.cursor()

        # Преобразуем список блюд в строку, разделенную запятыми
        items_str = ", ".join(self.items)

        # Исправленный SQL-запрос: включаем столбец total с его значением
        cursor.execute('''INSERT INTO orders (table_id, items, total)
                          VALUES (?, ?, ?)''', (self.table_id, items_str, self.total))

        conn.commit()
        conn.close()

    @staticmethod
    def get_order_by_table(table_id):
        """Получаем заказ для данного столика из базы данных."""
        conn = connect()
        cursor = conn.cursor()

        cursor.execute('''SELECT items FROM orders WHERE table_id = ?''', (table_id,))
        result = cursor.fetchone()

        conn.close()

        if result:
            return result[0]  # Возвращаем список блюд как строку
        return None
