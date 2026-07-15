import tkinter as tk
from tkinter import ttk, messagebox
from gui.sidebar import Sidebar
from gui.scanner_page import ScannerPage
from gui.quarantine_page import QuarantinePage
from gui.protection_page import ProtectionPage
from gui.settings_page import SettingsPage
from gui.modern_dashboard import ModernBackground
from engine.update_manager import create_initial_signatures
from services.startup_manager import StartupManager
from engine.scheduler import ScanScheduler
from cloud.virustotal import VirusTotalAPI
from database.db_manager import DatabaseManager
import os
import json
from datetime import datetime


class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ Nexus Antivirus - Ultimate Protection")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1a1a1a")
        self.root.minsize(1000, 600)
        
        # Initialize services
        self.initialize_services()
        
        # Load data
        self.scan_stats = self.load_scan_stats()
        self.protection_status = self.load_protection_status()
        
        # Create main container
        self.main_container = tk.Frame(root, bg="#1a1a1a")
        self.main_container.pack(fill="both", expand=True)
        
        # Create canvas for background
        self.bg_canvas = tk.Canvas(
            self.main_container,
            bg="#1a1a1a",
            highlightthickness=0
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Start modern background
        self.background = ModernBackground(
            self.bg_canvas,
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight()
        )
        
        # Create content frame (on top of background)
        self.content_frame = tk.Frame(
            self.main_container,
            bg="#1a1a1a",
            relief="flat"
        )
        self.content_frame.pack(fill="both", expand=True)
        
        # Main content area
        self.content = tk.Frame(
            self.content_frame,
            bg="#1a1a1a"
        )
        self.content.pack(side="right", expand=True, fill="both")
        
        # Sidebar
        self.sidebar = Sidebar(self.content_frame, self)
        
        # Show dashboard
        self.show_dashboard()
        
        # Bind resize
        self.root.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event):
        """Handle window resize"""
        if hasattr(self, 'background'):
            self.background.width = event.width
            self.background.height = event.height
    
    def initialize_services(self):
        """Initialize background services"""
        try:
            create_initial_signatures()
        except:
            pass
        
        try:
            self.startup_manager = StartupManager()
        except:
            self.startup_manager = None
        
        try:
            self.scheduler = ScanScheduler(callback=self.on_schedule_event)
            self.scheduler.start_scheduler()
        except:
            self.scheduler = None
        
        try:
            self.db = DatabaseManager()
        except:
            self.db = None
        
        try:
            self.virustotal = VirusTotalAPI()
        except:
            self.virustotal = None
        
        try:
            from gui.tray_icon import SystemTray
            self.tray = SystemTray(self)
            self.tray.show_tray()
        except:
            pass
    
    def on_schedule_event(self, message, message_type):
        print(f"[Scheduler] {message}")
    
    def load_scan_stats(self):
        stats_file = "data/scan_stats.json"
        default_stats = {
            "total_scans": 0,
            "total_files_scanned": 0,
            "total_threats_found": 0,
            "last_scan": "Never"
        }
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    return json.load(f)
            else:
                os.makedirs("data", exist_ok=True)
                with open(stats_file, 'w') as f:
                    json.dump(default_stats, f, indent=2)
                return default_stats
        except:
            return default_stats
    
    def load_protection_status(self):
        try:
            settings_file = "data/settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get("protection", {}).get("realtime_enabled", True)
            return True
        except:
            return True
    
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()
    
    def get_quarantine_count(self):
        try:
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            quarantine_dir = os.path.join(app_data, 'NexusAntivirus', 'quarantine')
            index_file = os.path.join(quarantine_dir, "index.json")
            if os.path.exists(index_file):
                with open(index_file, 'r') as f:
                    items = json.load(f)
                    return str(len(items))
        except:
            pass
        return "0"
    
    def show_dashboard(self):
        self.clear_content()
        
        # Main dashboard with modern design
        dashboard_frame = tk.Frame(self.content, bg="#1a1a1a")
        dashboard_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = tk.Frame(dashboard_frame, bg="#1a1a1a")
        header_frame.pack(fill="x", pady=30)
        
        tk.Label(
            header_frame,
            text="🛡️ NEXUS SECURITY CENTER",
            bg="#1a1a1a",
            fg="cyan",
            font=("Segoe UI", 32, "bold")
        ).pack()
        
        tk.Label(
            header_frame,
            text="AI-Powered Protection • Real-Time Security • Cloud Intelligence",
            bg="#1a1a1a",
            fg="#00ff88",
            font=("Segoe UI", 13)
        ).pack(pady=5)
        
        # Stats Cards
        stats_frame = tk.Frame(dashboard_frame, bg="#1a1a1a")
        stats_frame.pack(pady=25)
        
        protection_status = "🟢 Active" if self.protection_status else "🔴 Disabled"
        protection_color = "#00ff88" if self.protection_status else "#ff4444"
        
        db_stats = self.db.get_stats() if hasattr(self, 'db') and self.db else {}
        
        stats = [
            ("🛡️ Protection", protection_status, protection_color, "#00ff88"),
            ("📁 Files Scanned", f"{self.scan_stats['total_files_scanned']:,}", "#00aaff", "#00aaff"),
            ("⚠️ Threats", f"{db_stats.get('total_threats', self.scan_stats['total_threats_found'])}", "#ff8800", "#ff8800"),
            ("🔄 Last Scan", self.scan_stats['last_scan'], "#888888", "#666666"),
            ("📊 Total Scans", f"{db_stats.get('total_scans', self.scan_stats['total_scans'])}", "#aa66ff", "#aa66ff"),
            ("📦 Quarantine", f"{db_stats.get('quarantined', self.get_quarantine_count())}", "#ff6600", "#ff6600")
        ]
        
        for i, (label, value, color, border_color) in enumerate(stats):
            card = tk.Frame(
                stats_frame,
                bg="#222222",
                relief="ridge",
                bd=2,
                highlightbackground=border_color,
                highlightthickness=2
            )
            card.grid(row=i//3, column=i%3, padx=15, pady=10, ipadx=30, ipady=8)
            
            tk.Label(
                card,
                text=label,
                bg="#222222",
                fg="#888888",
                font=("Segoe UI", 11)
            ).pack()
            
            label_widget = tk.Label(
                card,
                text=value,
                bg="#222222",
                fg=color,
                font=("Segoe UI", 20, "bold")
            )
            label_widget.pack()
            
            # Store protection label for updates
            if label == "🛡️ Protection":
                self.protection_status_label = label_widget
        
        # Quick Actions
        actions_frame = tk.Frame(dashboard_frame, bg="#1a1a1a")
        actions_frame.pack(pady=20)
        
        quick_actions = [
            ("⚡ Quick Scan", self.show_scanner, "#0066cc", "Fast system scan"),
            ("🔍 Full Scan", self.show_scanner, "#cc6600", "Complete system scan"),
            ("📋 Quarantine", self.show_quarantine, "#ff8800", "Manage threats"),
            ("⚙️ Settings", self.show_settings, "#333333", "Configure app"),
            ("🔃 Update", self.show_settings, "#339933", "Check for updates")
        ]
        
        for text, command, color, tooltip in quick_actions:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                width=18,
                height=2,
                bg=color,
                fg="white",
                font=("Segoe UI", 12, "bold"),
                cursor="hand2",
                relief="raised"
            )
            btn.pack(side="left", padx=10)
        
        # Status Bar
        status_bar = tk.Frame(dashboard_frame, bg="#111111")
        status_bar.pack(side="bottom", fill="x", pady=15)
        
        # Left
        status_left = tk.Frame(status_bar, bg="#111111")
        status_left.pack(side="left", padx=20)
        
        status_text = "✅ System Protected" if self.protection_status else "⚠️ Protection Disabled"
        status_color = "#00ff88" if self.protection_status else "#ff8800"
        
        tk.Label(
            status_left,
            text=status_text,
            bg="#111111",
            fg=status_color,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        
        tk.Label(
            status_left,
            text="| v2.0",
            bg="#111111",
            fg="#666666",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=10)
        
        # Center
        status_center = tk.Frame(status_bar, bg="#111111")
        status_center.pack(side="left", padx=20)
        
        scheduler_status = "🔄 Scheduler: Running" if self.scheduler else "⏹️ Scheduler: Stopped"
        tk.Label(
            status_center,
            text=scheduler_status,
            bg="#111111",
            fg="#888888",
            font=("Segoe UI", 9)
        ).pack(side="left", padx=10)
        
        # Right
        status_right = tk.Frame(status_bar, bg="#111111")
        status_right.pack(side="right", padx=20)
        
        try:
            from engine.update_manager import UpdateManager
            um = UpdateManager()
            if um.check_for_updates().get('available', False):
                update_status = "⬇️ Update Available!"
                update_color = "#ff8800"
            else:
                update_status = "✅ Up to date"
                update_color = "#00ff88"
        except:
            update_status = "✅ Up to date"
            update_color = "#00ff88"
        
        tk.Label(
            status_right,
            text=f"🔄 {update_status}",
            bg="#111111",
            fg=update_color,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=10)
        
        # Database status
        db_status = "💾 DB: Connected" if self.db else "💾 DB: Disconnected"
        tk.Label(
            status_right,
            text=db_status,
            bg="#111111",
            fg="#00ff88" if self.db else "#ff4444",
            font=("Segoe UI", 9)
        ).pack(side="left", padx=10)
    
    def update_protection_status(self, enabled):
        self.protection_status = enabled
        if hasattr(self, 'protection_status_label'):
            try:
                if enabled:
                    self.protection_status_label.config(text="🟢 Active", fg="#00ff88")
                else:
                    self.protection_status_label.config(text="🔴 Disabled", fg="#ff4444")
            except:
                pass
    
    def show_scanner(self):
        self.clear_content()
        try:
            page = ScannerPage(self.content)
            page.frame.pack(expand=True, fill="both")
        except Exception as e:
            self.show_error(f"Failed to load Scanner: {str(e)}")
    
    def show_protection(self):
        self.clear_content()
        try:
            page = ProtectionPage(self.content)
            page.frame.pack(expand=True, fill="both")
        except Exception as e:
            self.show_error(f"Failed to load Protection: {str(e)}")
    
    def show_quarantine(self):
        self.clear_content()
        try:
            page = QuarantinePage(self.content)
            page.frame.pack(expand=True, fill="both")
        except Exception as e:
            self.show_error(f"Failed to load Quarantine: {str(e)}")
    
    def show_settings(self):
        self.clear_content()
        try:
            page = SettingsPage(self.content)
            page.frame.pack(expand=True, fill="both")
        except Exception as e:
            self.show_error(f"Failed to load Settings: {str(e)}")
    
    def show_error(self, message):
        tk.Label(
            self.content,
            text=f"❌ {message}",
            bg="#1a1a1a",
            fg="#ff4444",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=100)


def start_dashboard():
    root = tk.Tk()
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    app = Dashboard(root)
    root.mainloop()