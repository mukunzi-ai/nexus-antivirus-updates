import tkinter as tk

from gui.sidebar import Sidebar
from gui.scanner_page import ScannerPage
from gui.quarantine_page import QuarantinePage
from gui.protection_page import ProtectionPage



class Dashboard:

    def __init__(self, root):

        self.root = root

        self.root.title("Nexus Beta Antivirus")
        self.root.geometry("1000x600")
        self.root.configure(bg="#1a1a1a")


        # Main content area
        self.content = tk.Frame(
            root,
            bg="#1a1a1a"
        )

        self.content.pack(
            side="right",
            expand=True,
            fill="both"
        )


        # Sidebar
        self.sidebar = Sidebar(
            root,
            self
        )


        self.show_dashboard()



    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()



    def show_dashboard(self):

        self.clear_content()

        tk.Label(
            self.content,
            text="NEXUS BETA SECURITY CENTER",
            bg="#1a1a1a",
            fg="cyan",
            font=("Arial",26,"bold")
        ).pack(pady=80)



    def show_scanner(self):

        self.clear_content()

        page = ScannerPage(self.content)

        page.frame.pack(
            expand=True,
            fill="both"
        )



    def show_protection(self):

        self.clear_content()

        page = ProtectionPage(self.content)

        page.frame.pack(
            expand=True,
            fill="both"
        )



    def show_quarantine(self):

        self.clear_content()

        page = QuarantinePage(self.content)

        page.frame.pack(
            expand=True,
            fill="both"
        )



    def show_settings(self):

        self.clear_content()

        tk.Label(
            self.content,
            text="Settings",
            bg="#1a1a1a",
            fg="white",
            font=("Arial",25)
        ).pack(pady=50)



# This keeps compatibility with your app.py

def start_dashboard():

    root = tk.Tk()

    app = Dashboard(root)

    root.mainloop()