# ==========================================================
# Nexus Beta Antivirus
# GUI - Part 1/4
# ==========================================================

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import threading
import os

from DesktopEngine.antivirus_engine import AntivirusEngine
from DesktopEngine.ai_detector import MalwareAI
from DesktopEngine.threat_database import ThreatDatabase
from DesktopEngine.quarantine import QuarantineManager


# ==========================================================
# Create Engine Objects
# ==========================================================

engine = AntivirusEngine()

ai = MalwareAI()

database = ThreatDatabase()

quarantine = QuarantineManager()


# ==========================================================
# Main Window
# ==========================================================

root = tk.Tk()

root.title("Nexus Beta Antivirus")

root.geometry("1200x750")

root.configure(bg="#101820")

root.minsize(1100,700)


# ==========================================================
# Colors
# ==========================================================

BACKGROUND = "#101820"

CARD = "#1B2838"

BUTTON = "#00C853"

BUTTON_HOVER = "#00E676"

TEXT = "white"

ACCENT = "#00BCD4"

WARNING = "#FF9800"

DANGER = "#FF1744"

SUCCESS = "#00E676"


# ==========================================================
# Fonts
# ==========================================================

TITLE_FONT = ("Segoe UI",30,"bold")

HEADER_FONT = ("Segoe UI",16,"bold")

NORMAL_FONT = ("Segoe UI",11)

SMALL_FONT = ("Segoe UI",9)


# ==========================================================
# Variables
# ==========================================================

selected_folder = tk.StringVar()

status_text = tk.StringVar()

status_text.set("Status : Ready")


files_scanned = tk.IntVar(value=0)

threats_found = tk.IntVar(value=0)

safe_files = tk.IntVar(value=0)


# ==========================================================
# Title
# ==========================================================

title = tk.Label(

    root,

    text="NEXUS BETA",

    fg=ACCENT,

    bg=BACKGROUND,

    font=TITLE_FONT

)

title.pack(pady=15)


subtitle = tk.Label(

    root,

    text="Professional Antivirus Prototype",

    fg="white",

    bg=BACKGROUND,

    font=("Segoe UI",11)

)

subtitle.pack()


# ==========================================================
# Dashboard
# ==========================================================

dashboard = tk.Frame(

    root,

    bg=BACKGROUND

)

dashboard.pack(fill="x",padx=20,pady=20)


# ==========================================================
# Card Builder
# ==========================================================

def create_card(title_text, variable, color):

    frame = tk.Frame(

        dashboard,

        bg=CARD,

        width=240,

        height=120,

        highlightbackground=color,

        highlightthickness=2

    )

    frame.pack(side="left",expand=True,padx=10)

    frame.pack_propagate(False)


    tk.Label(

        frame,

        text=title_text,

        bg=CARD,

        fg="white",

        font=HEADER_FONT

    ).pack(pady=(18,5))


    tk.Label(

        frame,

        textvariable=variable,

        bg=CARD,

        fg=color,

        font=("Segoe UI",28,"bold")

    ).pack()


    return frame


create_card(

    "Files Scanned",

    files_scanned,

    ACCENT

)

create_card(

    "Threats Found",

    threats_found,

    DANGER

)

create_card(

    "Safe Files",

    safe_files,

    SUCCESS

)

# ==========================================================
# Controls
# ==========================================================

controls = tk.Frame(
    root,
    bg=BACKGROUND
)

controls.pack(fill="x", padx=20)


def browse_folder():

    folder = filedialog.askdirectory()

    if folder:

        selected_folder.set(folder)

        status_text.set("Selected: " + folder)


folder_entry = tk.Entry(

    controls,

    textvariable=selected_folder,

    font=NORMAL_FONT,

    width=70

)

folder_entry.pack(

    side="left",

    padx=10,

    pady=10,

    ipady=5

)


browse_button = tk.Button(

    controls,

    text="Browse",

    bg=BUTTON,

    fg="white",

    activebackground=BUTTON_HOVER,

    font=HEADER_FONT,

    relief="flat",

    command=browse_folder

)

browse_button.pack(

    side="left",

    padx=5

)


scan_button = tk.Button(

    controls,

    text="Full Scan",

    bg=ACCENT,

    fg="white",

    font=HEADER_FONT,

    relief="flat"

)

scan_button.pack(

    side="left",

    padx=5

)


quick_button = tk.Button(

    controls,

    text="Quick Scan",

    bg=WARNING,

    fg="white",

    font=HEADER_FONT,

    relief="flat"

)

quick_button.pack(

    side="left",

    padx=5

)



# ==========================================================
# Progress Bar
# ==========================================================

progress_frame = tk.Frame(

    root,

    bg=BACKGROUND

)

progress_frame.pack(

    fill="x",

    padx=20,

    pady=(10,5)

)


progress = ttk.Progressbar(

    progress_frame,

    orient="horizontal",

    mode="determinate",

    length=1000

)

progress.pack(

    fill="x"

)



# ==========================================================
# Results Area
# ==========================================================

results_frame = tk.Frame(

    root,

    bg=BACKGROUND

)

results_frame.pack(

    fill="both",

    expand=True,

    padx=20,

    pady=10

)


columns = (

    "File",

    "Prediction",

    "Confidence"

)


tree = ttk.Treeview(

    results_frame,

    columns=columns,

    show="headings",

    height=18

)


tree.heading(

    "File",

    text="File"

)

tree.heading(

    "Prediction",

    text="Prediction"

)

tree.heading(

    "Confidence",

    text="Confidence"

)


tree.column(

    "File",

    width=700

)

tree.column(

    "Prediction",

    width=180,

    anchor="center"

)

tree.column(

    "Confidence",

    width=120,

    anchor="center"

)


scrollbar = ttk.Scrollbar(

    results_frame,

    orient="vertical",

    command=tree.yview

)

tree.configure(

    yscrollcommand=scrollbar.set

)


tree.pack(

    side="left",

    fill="both",

    expand=True

)

scrollbar.pack(

    side="right",

    fill="y"

)



# ==========================================================
# Status Bar
# ==========================================================

status_bar = tk.Label(

    root,

    textvariable=status_text,

    bg=CARD,

    fg="white",

    font=SMALL_FONT,

    anchor="w"

)

status_bar.pack(

    side="bottom",

    fill="x"

)
