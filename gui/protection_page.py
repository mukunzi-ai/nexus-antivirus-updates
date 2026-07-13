import tkinter as tk


class ProtectionPage:

    def __init__(self, parent):

        self.frame = tk.Frame(
            parent,
            bg="#1a1a1a"
        )

        tk.Label(
            self.frame,
            text="Real-Time Protection",
            bg="#1a1a1a",
            fg="lime",
            font=("Arial",26,"bold")
        ).pack(pady=50)
