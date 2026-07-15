import tkinter as tk


class Sidebar:

    def __init__(self, parent, controller):

        self.parent = parent
        self.controller = controller

        # Sidebar container
        self.frame = tk.Frame(
            parent,
            bg="#111111",
            width=220
        )

        self.frame.pack(
            side="left",
            fill="y"
        )

        self.create_logo()
        self.create_buttons()

    def create_logo(self):

        logo = tk.Label(
            self.frame,
            text="NEXUS\nBETA",
            bg="#111111",
            fg="cyan",
            font=("Arial", 20, "bold")
        )

        logo.pack(
            pady=30
        )

    def create_buttons(self):

        buttons = [
            ("🏠 Dashboard", self.controller.show_dashboard),
            ("🔍 Scanner", self.controller.show_scanner),
            ("🛡 Protection", self.controller.show_protection),
            ("📁 Quarantine", self.controller.show_quarantine),
            ("⚙️ Settings", self.controller.show_settings)
        ]

        for text, command in buttons:
            btn = tk.Button(
                self.frame,
                text=text,
                command=command,
                width=18,
                height=2,
                bg="#222222",
                fg="white",
                activebackground="#00aaaa",
                activeforeground="white",
                relief="flat",
                font=("Arial", 11)
            )

            btn.pack(
                pady=8,
                padx=10
            )