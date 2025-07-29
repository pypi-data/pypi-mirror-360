# hiplt/gui.py

import tkinter as tk
from tkinter import messagebox


class GUIApp:
    """
    Минималистичный графический интерфейс на Tkinter для CSO.
    Можно расширить в будущем под Kivy или webview.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CSO GUI")
        self.root.geometry("400x200")
        self._build_ui()

    def _build_ui(self):
        self.label = tk.Label(self.root, text="Добро пожаловать в CSO GUI!", font=("Arial", 14))
        self.label.pack(pady=20)

        self.btn_hello = tk.Button(self.root, text="Нажми меня", command=self.say_hello)
        self.btn_hello.pack(pady=10)

        self.btn_quit = tk.Button(self.root, text="Выход", command=self.root.quit)
        self.btn_quit.pack(pady=10)

    def say_hello(self):
        messagebox.showinfo("Привет", "Привет из CSO GUI!")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GUIApp()
    app.run()