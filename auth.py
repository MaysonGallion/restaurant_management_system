import tkinter as tk
from tkinter import messagebox
from database import connect


class AuthWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success

        # окно авторизации
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("300x200")

        # Логин
        tk.Label(self.root, text="login:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        # Пароль
        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Enter", command=self.login).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Enter your username and password!")
            return

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            messagebox.showinfo("Success", "Authorization was successful!")
            self.root.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def run(self):
        self.root.mainloop()


