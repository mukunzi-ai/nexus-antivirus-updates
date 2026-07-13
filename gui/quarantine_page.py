import tkinter as tk


class QuarantinePage:

    def __init__(self, parent):

        self.frame = tk.Frame(
            parent,
            bg="#1a1a1a"
        )

        tk.Label(
            self.frame,
            text="Quarantine Manager",
            bg="#1a1a1a",
            fg="orange",
            font=("Arial",26,"bold")
        ).pack(pady=50)
