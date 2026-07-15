import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from engine.update_manager import UpdateManager
from engine.scheduler import ScanScheduler
from services.startup_manager import StartupManager
from cloud.virustotal import VirusTotalAPI


class SettingsPage:
    def __init__(self, parent):
        self.parent = parent
        self.settings_file = "data/settings.json"
        self.settings = self.load_settings()
        
        # Initialize managers
        self.update_manager = UpdateManager()
        self.scheduler = ScanScheduler()
        self.startup_manager = StartupManager()
        
        self.frame = tk.Frame(parent, bg="#1a1a1a")
        
        # Title
        title = tk.Label(
            self.frame,
            text="⚙️ Settings",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 26, "bold")
        )
        title.pack(pady=20)
        
        # Create Notebook (tabs)
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(pady=15, padx=50, fill="both", expand=True)
        
        # Tab 1: Scan Settings
        self.scan_tab = tk.Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(self.scan_tab, text="Scan Settings")
        self.build_scan_tab()
        
        # Tab 2: Protection Settings
        self.protection_tab = tk.Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(self.protection_tab, text="Protection")
        self.build_protection_tab()
        
        # Tab 3: Schedule Settings
        self.schedule_tab = tk.Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(self.schedule_tab, text="Schedule")
        self.build_schedule_tab()
        
        # Tab 4: Updates
        self.updates_tab = tk.Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(self.updates_tab, text="Updates")
        self.build_updates_tab()
        
        # Tab 5: Cloud
        self.cloud_tab = tk.Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(self.cloud_tab, text="Cloud")
        self.build_cloud_tab()
        
        # Tab 6: Startup
        self.startup_tab = tk.Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(self.startup_tab, text="Startup")
        self.build_startup_tab()
        
        # Tab 7: About
        self.about_tab = tk.Frame(self.notebook, bg="#1a1a1a")
        self.notebook.add(self.about_tab, text="About")
        self.build_about_tab()
    
    def load_settings(self):
        """Load settings from JSON file"""
        default_settings = {
            "scan": {
                "max_file_size": 100,
                "scan_archives": True,
                "excluded_extensions": [".tmp", ".log"],
                "excluded_folders": []
            },
            "protection": {
                "realtime_enabled": True,
                "monitor_downloads": True,
                "monitor_usb": True
            },
            "schedule": {
                "quick_scan": "daily",
                "full_scan": "weekly",
                "time": "02:00"
            },
            "cloud": {
                "virustotal_enabled": False,
                "auto_upload": False
            },
            "startup": {
                "enabled": False,
                "minimized": True
            }
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    for key in default_settings:
                        if key not in loaded:
                            loaded[key] = default_settings[key]
                    return loaded
            else:
                os.makedirs("data", exist_ok=True)
                with open(self.settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                return default_settings
        except:
            return default_settings
    
    def auto_save(self):
        """Auto-save settings immediately"""
        try:
            # Collect values
            self.settings["scan"]["max_file_size"] = int(self.max_size_var.get())
            self.settings["scan"]["scan_archives"] = self.scan_archives_var.get()
            self.settings["protection"]["realtime_enabled"] = self.realtime_var.get()
            self.settings["protection"]["monitor_downloads"] = self.monitor_downloads_var.get()
            if hasattr(self, 'monitor_usb_var'):
                self.settings["protection"]["monitor_usb"] = self.monitor_usb_var.get()
            self.settings["schedule"]["quick_scan"] = self.quick_scan_var.get()
            self.settings["schedule"]["full_scan"] = self.full_scan_var.get()
            self.settings["schedule"]["time"] = self.scan_time_var.get()
            if hasattr(self, 'startup_var'):
                self.settings["startup"]["enabled"] = self.startup_var.get()
            if hasattr(self, 'vt_enabled_var'):
                self.settings["cloud"]["virustotal_enabled"] = self.vt_enabled_var.get()
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            if hasattr(self, 'startup_var'):
                if self.startup_var.get():
                    self.startup_manager.add_to_startup()
                else:
                    self.startup_manager.remove_from_startup()
            
            self.apply_protection_settings()
            
            return True
        except Exception as e:
            print(f"Auto-save error: {e}")
            return False
    
    def apply_protection_settings(self):
        """Apply protection settings in real-time"""
        try:
            if hasattr(self.parent, 'update_protection_status'):
                self.parent.update_protection_status(self.realtime_var.get())
        except:
            pass
    
    def on_setting_change(self, *args):
        """Called when any setting changes - auto-save"""
        self.auto_save()
    
    def build_scan_tab(self):
        """Build scan settings tab"""
        # Max file size
        row = tk.Frame(self.scan_tab, bg="#1a1a1a")
        row.pack(pady=15, fill="x", padx=20)
        
        tk.Label(
            row,
            text="Max File Size (MB):",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 12)
        ).pack(side="left")
        
        self.max_size_var = tk.StringVar(value=str(self.settings["scan"]["max_file_size"]))
        self.max_size_var.trace_add("write", self.on_setting_change)
        entry = tk.Entry(
            row,
            textvariable=self.max_size_var,
            width=10,
            bg="#333",
            fg="white"
        )
        entry.pack(side="left", padx=10)
        
        tk.Label(
            row,
            text="(Skip files larger than this)",
            bg="#1a1a1a",
            fg="gray",
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        # Scan archives
        row2 = tk.Frame(self.scan_tab, bg="#1a1a1a")
        row2.pack(pady=15, fill="x", padx=20)
        
        self.scan_archives_var = tk.BooleanVar(value=self.settings["scan"]["scan_archives"])
        self.scan_archives_var.trace_add("write", self.on_setting_change)
        cb = tk.Checkbutton(
            row2,
            text="Scan inside archives (.zip, .rar, .7z)",
            variable=self.scan_archives_var,
            bg="#1a1a1a",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 12),
            command=self.on_setting_change
        )
        cb.pack(side="left")
        
        # Excluded folders
        row3 = tk.Frame(self.scan_tab, bg="#1a1a1a")
        row3.pack(pady=15, fill="x", padx=20)
        
        tk.Label(
            row3,
            text="Excluded Folders:",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 12)
        ).pack(anchor="w")
        
        self.excluded_listbox = tk.Listbox(
            row3,
            bg="#333",
            fg="white",
            height=4
        )
        self.excluded_listbox.pack(fill="x", pady=5)
        
        for folder in self.settings["scan"]["excluded_folders"]:
            self.excluded_listbox.insert("end", folder)
        
        btn_frame = tk.Frame(row3, bg="#1a1a1a")
        btn_frame.pack()
        
        tk.Button(
            btn_frame,
            text="Add Folder",
            command=self.add_excluded_folder,
            bg="#333",
            fg="white",
            width=12,
            cursor="hand2"
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="Remove Selected",
            command=self.remove_excluded_folder,
            bg="#cc0000",
            fg="white",
            width=15,
            cursor="hand2"
        ).pack(side="left", padx=5)
    
    def build_protection_tab(self):
        """Build protection settings tab with real-time toggling"""
        options = [
            ("realtime_var", "🛡️ Enable Real-Time Protection", self.settings["protection"]["realtime_enabled"]),
            ("monitor_downloads_var", "📁 Monitor Downloads Folder", self.settings["protection"]["monitor_downloads"]),
            ("monitor_usb_var", "💾 Auto-Scan USB Drives", self.settings["protection"].get("monitor_usb", True))
        ]
        
        for var_name, label, default in options:
            row = tk.Frame(self.protection_tab, bg="#1a1a1a")
            row.pack(pady=10, fill="x", padx=20)
            
            setattr(self, var_name, tk.BooleanVar(value=default))
            getattr(self, var_name).trace_add("write", self.on_setting_change)
            
            cb = tk.Checkbutton(
                row,
                text=label,
                variable=getattr(self, var_name),
                bg="#1a1a1a",
                fg="white",
                selectcolor="#1a1a1a",
                font=("Segoe UI", 12),
                command=self.on_setting_change
            )
            cb.pack(side="left")
    
    def build_schedule_tab(self):
        """Build schedule settings tab"""
        # Quick scan frequency
        row1 = tk.Frame(self.schedule_tab, bg="#1a1a1a")
        row1.pack(pady=15, fill="x", padx=20)
        
        tk.Label(
            row1,
            text="Quick Scan:",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 12)
        ).pack(side="left")
        
        self.quick_scan_var = tk.StringVar(value=self.settings["schedule"]["quick_scan"])
        self.quick_scan_var.trace_add("write", self.on_setting_change)
        options = ["disabled", "daily", "weekly"]
        ttk.Combobox(
            row1,
            textvariable=self.quick_scan_var,
            values=options,
            width=15,
            state="readonly"
        ).pack(side="left", padx=10)
        
        # Full scan frequency
        row2 = tk.Frame(self.schedule_tab, bg="#1a1a1a")
        row2.pack(pady=15, fill="x", padx=20)
        
        tk.Label(
            row2,
            text="Full Scan:",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 12)
        ).pack(side="left")
        
        self.full_scan_var = tk.StringVar(value=self.settings["schedule"]["full_scan"])
        self.full_scan_var.trace_add("write", self.on_setting_change)
        ttk.Combobox(
            row2,
            textvariable=self.full_scan_var,
            values=["disabled", "weekly", "monthly"],
            width=15,
            state="readonly"
        ).pack(side="left", padx=10)
        
        # Scan time
        row3 = tk.Frame(self.schedule_tab, bg="#1a1a1a")
        row3.pack(pady=15, fill="x", padx=20)
        
        tk.Label(
            row3,
            text="Scan Time (24h):",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 12)
        ).pack(side="left")
        
        self.scan_time_var = tk.StringVar(value=self.settings["schedule"]["time"])
        self.scan_time_var.trace_add("write", self.on_setting_change)
        entry = tk.Entry(
            row3,
            textvariable=self.scan_time_var,
            width=10,
            bg="#333",
            fg="white"
        )
        entry.pack(side="left", padx=10)
        
        tk.Label(
            row3,
            text="(Format: HH:MM)",
            bg="#1a1a1a",
            fg="gray",
            font=("Segoe UI", 10)
        ).pack(side="left")
    
    def build_updates_tab(self):
        """Build updates tab"""
        # Current status
        status_frame = tk.Frame(self.updates_tab, bg="#1a1a1a")
        status_frame.pack(pady=20, fill="x", padx=20)
        
        tk.Label(
            status_frame,
            text="📊 Update Status",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")
        
        # Status info
        info_frame = tk.Frame(self.updates_tab, bg="#222222", relief="groove", bd=2)
        info_frame.pack(pady=10, fill="x", padx=20, ipady=10)
        
        self.version_label = tk.Label(
            info_frame,
            text=f"Current Version: {self.update_manager.current_version}",
            bg="#222222",
            fg="#00ff88",
            font=("Segoe UI", 12)
        )
        self.version_label.pack(anchor="w", padx=20, pady=5)
        
        self.signature_count_label = tk.Label(
            info_frame,
            text=f"Signatures: {self.update_manager.get_signature_count()}",
            bg="#222222",
            fg="white",
            font=("Segoe UI", 12)
        )
        self.signature_count_label.pack(anchor="w", padx=20, pady=5)
        
        self.last_update_label = tk.Label(
            info_frame,
            text=f"Last Update: {self.update_manager.get_last_update_time()}",
            bg="#222222",
            fg="white",
            font=("Segoe UI", 12)
        )
        self.last_update_label.pack(anchor="w", padx=20, pady=5)
        
        self.auto_update_label = tk.Label(
            info_frame,
            text=f"Auto-Update: {'Enabled' if self.update_manager.running else 'Disabled'}",
            bg="#222222",
            fg="#00ff88" if self.update_manager.running else "#ff8800",
            font=("Segoe UI", 12)
        )
        self.auto_update_label.pack(anchor="w", padx=20, pady=5)
        
        # Progress bar for update
        self.update_progress = ttk.Progressbar(
            self.updates_tab,
            length=400,
            mode='determinate'
        )
        self.update_progress.pack(pady=10)
        
        self.update_status_label = tk.Label(
            self.updates_tab,
            text="",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 11)
        )
        self.update_status_label.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.updates_tab, bg="#1a1a1a")
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="🔍 Check for Updates",
            command=self.check_updates,
            width=20,
            height=2,
            bg="#0066cc",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="⬇️ Download Updates",
            command=self.download_updates,
            width=20,
            height=2,
            bg="#339933",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="🔄 Rollback",
            command=self.rollback_update,
            width=15,
            height=2,
            bg="#cc6600",
            fg="white",
            font=("Segoe UI", 11),
            cursor="hand2"
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="📂 Open Folder",
            command=self.open_update_folder,
            width=15,
            height=2,
            bg="#444444",
            fg="white",
            font=("Segoe UI", 11),
            cursor="hand2"
        ).pack(side="left", padx=10)
    
    def build_cloud_tab(self):
        """Build cloud scanning tab"""
        # VirusTotal integration
        info_frame = tk.Frame(self.cloud_tab, bg="#222222", relief="groove", bd=2)
        info_frame.pack(pady=10, fill="x", padx=20, ipady=10)
        
        tk.Label(
            info_frame,
            text="☁️ VirusTotal Cloud Integration",
            bg="#222222",
            fg="#00ff88",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=5)
        
        tk.Label(
            info_frame,
            text="Scan files with 70+ antivirus engines in the cloud",
            bg="#222222",
            fg="white",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=5)
        
        # Enable/disable
        row = tk.Frame(self.cloud_tab, bg="#1a1a1a")
        row.pack(pady=15, fill="x", padx=20)
        
        self.vt_enabled_var = tk.BooleanVar(value=self.settings["cloud"].get("virustotal_enabled", False))
        self.vt_enabled_var.trace_add("write", self.on_setting_change)
        cb = tk.Checkbutton(
            row,
            text="Enable VirusTotal Cloud Scanning",
            variable=self.vt_enabled_var,
            bg="#1a1a1a",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 12),
            command=self.on_setting_change
        )
        cb.pack(side="left")
        
        # API Key entry
        key_frame = tk.Frame(self.cloud_tab, bg="#1a1a1a")
        key_frame.pack(pady=15, fill="x", padx=20)
        
        tk.Label(
            key_frame,
            text="VirusTotal API Key:",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 12)
        ).pack(anchor="w")
        
        api_key = ""
        try:
            if os.path.exists("data/vt_key.txt"):
                with open("data/vt_key.txt", 'r') as f:
                    api_key = f.read().strip()
        except:
            pass
        
        self.vt_api_key = tk.Entry(
            key_frame,
            bg="#333",
            fg="white",
            width=50,
            show="*"
        )
        self.vt_api_key.pack(anchor="w", pady=5)
        if api_key:
            self.vt_api_key.insert(0, api_key)
        else:
            self.vt_api_key.insert(0, "Enter your API key here")
        
        tk.Label(
            key_frame,
            text="Get your free API key at: https://www.virustotal.com/gui/join-us",
            bg="#1a1a1a",
            fg="gray",
            font=("Segoe UI", 9)
        ).pack(anchor="w")
        
        btn_frame = tk.Frame(self.cloud_tab, bg="#1a1a1a")
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="💾 Save API Key",
            command=self.save_vt_key,
            width=15,
            height=1,
            bg="#0066cc",
            fg="white",
            font=("Segoe UI", 11),
            cursor="hand2"
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame,
            text="🔍 Test Connection",
            command=self.test_vt_connection,
            width=15,
            height=1,
            bg="#339933",
            fg="white",
            font=("Segoe UI", 11),
            cursor="hand2"
        ).pack(side="left", padx=10)
    
    def build_startup_tab(self):
        """Build startup settings tab"""
        info_frame = tk.Frame(self.startup_tab, bg="#222222", relief="groove", bd=2)
        info_frame.pack(pady=10, fill="x", padx=20, ipady=10)
        
        tk.Label(
            info_frame,
            text="🚀 Startup with Windows",
            bg="#222222",
            fg="#00ff88",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=20, pady=5)
        
        tk.Label(
            info_frame,
            text="Automatically start Nexus Antivirus when Windows boots",
            bg="#222222",
            fg="white",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=5)
        
        row = tk.Frame(self.startup_tab, bg="#1a1a1a")
        row.pack(pady=15, fill="x", padx=20)
        
        self.startup_var = tk.BooleanVar(value=self.startup_manager.is_in_startup())
        self.startup_var.trace_add("write", self.on_setting_change)
        cb = tk.Checkbutton(
            row,
            text="Start Nexus Antivirus with Windows",
            variable=self.startup_var,
            bg="#1a1a1a",
            fg="white",
            selectcolor="#1a1a1a",
            font=("Segoe UI", 12),
            command=self.on_setting_change
        )
        cb.pack(side="left")
        
        status_frame = tk.Frame(self.startup_tab, bg="#1a1a1a")
        status_frame.pack(pady=15, fill="x", padx=20)
        
        methods = self.startup_manager.get_startup_methods()
        status_text = "Active via: " + ", ".join(methods) if methods else "Not active"
        
        tk.Label(
            status_frame,
            text=f"Status: {status_text}",
            bg="#1a1a1a",
            fg="white" if methods else "gray",
            font=("Segoe UI", 11)
        ).pack(anchor="w")
        
        info2 = tk.Frame(self.startup_tab, bg="#1a1a1a")
        info2.pack(pady=15, fill="x", padx=20)
        
        tk.Label(
            info2,
            text="💡 Tip: Startup is added via Windows Registry and Startup Folder",
            bg="#1a1a1a",
            fg="gray",
            font=("Segoe UI", 10)
        ).pack(anchor="w")
    
    def build_about_tab(self):
        """Build about tab"""
        info = tk.Label(
            self.about_tab,
            text="🛡️ NEXUS ANTIVIRUS\n\nVersion: 2.0.0\n\n"
                 "Features:\n"
                 "• Multi-threaded Scanning\n"
                 "• Real-Time Protection\n"
                 "• Archive Scanning\n"
                 "• Memory Scanning\n"
                 "• Automatic Updates\n"
                 "• Quarantine Management\n"
                 "• Scheduled Scanning\n"
                 "• Cloud Integration\n"
                 "• System Tray\n"
                 "• Startup with Windows\n"
                 "• Auto-save Settings\n\n"
                 "Built with Python & Tkinter\n\n"
                 "© 2024 Nexus Security",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 14),
            justify="center"
        )
        info.pack(pady=50)
    
    def add_excluded_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.excluded_listbox.insert("end", folder)
            self.settings["scan"]["excluded_folders"].append(folder)
            self.auto_save()
    
    def remove_excluded_folder(self):
        selection = self.excluded_listbox.curselection()
        if selection:
            self.excluded_listbox.delete(selection[0])
            self.settings["scan"]["excluded_folders"].pop(selection[0])
            self.auto_save()
    
    def check_updates(self):
        self.update_status_label.config(text="Checking for updates...", fg="yellow")
        self.update_progress['value'] = 0
        
        result = self.update_manager.check_for_updates()
        
        if result.get('available', False):
            self.update_status_label.config(
                text=f"✅ Update available: v{result['version']} ({result['signature_count']} signatures)",
                fg="lime"
            )
            self.update_progress['value'] = 100
        elif 'error' in result:
            self.update_status_label.config(
                text=f"❌ Error: {result['error']}",
                fg="red"
            )
        else:
            self.update_status_label.config(
                text="✅ No updates available. You're up to date!",
                fg="lime"
            )
            self.update_progress['value'] = 100
    
    def download_updates(self):
        def update_callback(message, progress=None):
            self.update_status_label.config(text=message, fg="white")
            if progress is not None:
                self.update_progress['value'] = progress
            self.update_progress.update()
        
        self.update_status_label.config(text="Starting update...", fg="yellow")
        self.update_progress['value'] = 0
        
        import threading
        thread = threading.Thread(
            target=self._download_updates_thread,
            args=(update_callback,)
        )
        thread.start()
    
    def _download_updates_thread(self, callback):
        success, message = self.update_manager.download_updates(callback)
        
        if success:
            callback(f"✅ {message}", 100)
            self.version_label.config(text=f"Current Version: {self.update_manager.current_version}")
            self.signature_count_label.config(text=f"Signatures: {self.update_manager.get_signature_count()}")
            self.last_update_label.config(text=f"Last Update: {self.update_manager.get_last_update_time()}")
        else:
            callback(f"❌ {message}", 100)
    
    def rollback_update(self):
        if not messagebox.askyesno(
            "Confirm Rollback",
            "Are you sure you want to rollback to the previous version?"
        ):
            return
        
        success, message = self.update_manager.rollback_update()
        
        if success:
            messagebox.showinfo("Success", message)
            self.version_label.config(text=f"Current Version: {self.update_manager.current_version}")
            self.signature_count_label.config(text=f"Signatures: {self.update_manager.get_signature_count()}")
            self.last_update_label.config(text=f"Last Update: {self.update_manager.get_last_update_time()}")
        else:
            messagebox.showerror("Error", message)
    
    def open_update_folder(self):
        try:
            import subprocess
            update_path = self.update_manager.update_dir
            if os.path.exists(update_path):
                os.startfile(update_path) if os.name == 'nt' else subprocess.Popen(['xdg-open', update_path])
            else:
                messagebox.showinfo("Info", "Update folder doesn't exist yet.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
    
    def save_vt_key(self):
        key = self.vt_api_key.get().strip()
        if key and key != "Enter your API key here":
            try:
                os.environ['VIRUSTOTAL_API_KEY'] = key
                with open("data/vt_key.txt", 'w') as f:
                    f.write(key)
                messagebox.showinfo("Success", "API key saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save key: {str(e)}")
    
    def test_vt_connection(self):
        try:
            key = os.environ.get('VIRUSTOTAL_API_KEY', '')
            if not key and os.path.exists("data/vt_key.txt"):
                with open("data/vt_key.txt", 'r') as f:
                    key = f.read().strip()
                    os.environ['VIRUSTOTAL_API_KEY'] = key
            
            if not key or key == "Enter your API key here":
                messagebox.showwarning("No API Key", "Please enter your VirusTotal API key first.")
                return
            
            vt = VirusTotalAPI(key)
            result = vt.get_file_report("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
            
            if result and not result.get('error'):
                messagebox.showinfo("Success", "✅ Connected to VirusTotal API successfully!")
            else:
                messagebox.showerror("Error", f"Connection failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {str(e)}")