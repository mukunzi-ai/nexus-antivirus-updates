import tkinter as tk


class ScannerPage:

    def __init__(self, parent):

        self.frame = tk.Frame(
            parent,
            bg="#1a1a1a"
        )


        title = tk.Label(
            self.frame,
            text="Virus Scanner",
            bg="#1a1a1a",
            fg="cyan",
            font=("Arial",26,"bold")
        )

        title.pack(pady=50)


        scan_button = tk.Button(
            self.frame,
            text="Start Scan",
            width=20,
            height=2
        )

        scan_button.pack()