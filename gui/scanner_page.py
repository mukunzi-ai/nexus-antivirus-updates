import tkinter as tk
from tkinter import filedialog

from scanner.scanner import Scanner



class ScannerPage:

    def __init__(self, parent):

        self.scanner = Scanner()


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

        title.pack(pady=30)



        self.result = tk.Label(
            self.frame,
            text="Ready to scan",
            bg="#1a1a1a",
            fg="white",
            font=("Arial",14)
        )

        self.result.pack(pady=20)



        scan_button = tk.Button(
            self.frame,
            text="Select File & Scan",
            command=self.scan_file,
            width=20,
            height=2,
            bg="#222222",
            fg="white"
        )

        scan_button.pack(pady=20)



    def scan_file(self):

        file_path = filedialog.askopenfilename()


        if file_path:

            result = self.scanner.scan_file(file_path)


            message = (
                f"File:\n{result['file']}\n\n"
                f"Status: {result['status']}\n\n"
                f"SHA256:\n{result['hash']}"
            )


            self.result.config(
                text=message
            )
