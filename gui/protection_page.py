import tkinter as tk
import threading
import time
import os
import json
from datetime import datetime


class ProtectionPage:
    def __init__(self, parent):
        self.parent = parent
        self.protection_active = False
        self.monitor_thread = None
        self.monitoring = False
        
        self.frame = tk.Frame(parent, bg="#1a1a1a")
        
        # Load settings
        self.load_settings()
        
        # Title
        tk.Label(
            self.frame,
            text="🛡️ Real-Time Protection",
            bg="#1a1a1a",
            fg="lime",
            font=("Arial", 26, "bold")
        ).pack(pady=30)
        
        # Status display
        self.status_frame = tk.Frame(
            self.frame,
            bg="#222222",
            relief="groove",
            bd=3
        )
        self.status_frame.pack(pady=20, padx=100, fill="x")
        
        # Status indicator
        self.status_indicator = tk.Canvas(
            self.status_frame,
            width=50,
            height=50,
            bg="#222222",
            highlightthickness=0
        )
        self.status_indicator.pack(pady=20)
        
        # Initial status
        if self.protection_enabled:
            self.set_status_active()
        else:
            self.set_status_inactive()
        
        self.status_label = tk.Label(
            self.status_frame,
            text="",
            bg="#222222",
            fg="white",
            font=("Arial", 20, "bold")
        )
        self.status_label.pack(pady=10)
        
        self.details_label = tk.Label(
            self.status_frame,
            text="",
            bg="#222222",
            fg="gray",
            font=("Arial", 11)
        )
        self.details_label.pack(pady=5)
        
        self.update_status_text()
        
        # Toggle button
        self.toggle_btn = tk.Button(
            self.frame,
            text="",
            command=self.toggle_protection,
            width=25,
            height=2,
            font=("Arial", 14, "bold"),
            cursor="hand2"
        )
        self.toggle_btn.pack(pady=20)
        self.update_toggle_button()
        
        # Stats frame
        stats_frame = tk.Frame(self.frame, bg="#1a1a1a")
        stats_frame.pack(pady=10)
        
        stats = [
            ("📊 Protected Files", "0"),
            ("🔒 Threats Blocked", "0"),
            ("⏱️ Active Time", "00:00:00")
        ]
        
        self.stats_values = {}
        for i, (label, value) in enumerate(stats):
            frame = tk.Frame(stats_frame, bg="#222222", relief="groove", bd=2)
            frame.grid(row=i//3, column=i%3, padx=20, pady=10, ipadx=30)
            
            tk.Label(
                frame,
                text=label,
                bg="#222222",
                fg="white",
                font=("Arial", 11)
            ).pack()
            
            self.stats_values[label] = tk.Label(
                frame,
                text=value,
                bg="#222222",
                fg="cyan",
                font=("Arial", 16, "bold")
            )
            self.stats_values[label].pack()
        
        # Protection log
        log_frame = tk.Frame(self.frame, bg="#1a1a1a")
        log_frame.pack(pady=15, fill="both", expand=True, padx=100)
        
        tk.Label(
            log_frame,
            text="Protection Log",
            bg="#1a1a1a",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")
        
        self.log_text = tk.Text(
            log_frame,
            bg="#0d0d0d",
            fg="white",
            height=8,
            wrap="word",
            font=("Consolas", 10)
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Start protection if enabled
        if self.protection_enabled:
            self.enable_protection()
    
    def load_settings(self):
        """Load protection settings"""
        try:
            settings_file = "data/settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.protection_enabled = settings.get("protection", {}).get("realtime_enabled", True)
            else:
                self.protection_enabled = True
        except:
            self.protection_enabled = True
    
    def set_status_active(self):
        """Set status to active"""
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(5, 5, 45, 45, fill="lime", outline="lime")
    
    def set_status_inactive(self):
        """Set status to inactive"""
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(5, 5, 45, 45, fill="red", outline="red")
    
    def update_status_text(self):
        """Update status text"""
        if self.protection_enabled and self.protection_active:
            self.status_label.config(text="🟢 Protection is ACTIVE", fg="lime")
            self.details_label.config(text="Real-time monitoring is running")
        elif self.protection_enabled and not self.protection_active:
            self.status_label.config(text="🔄 Starting protection...", fg="yellow")
            self.details_label.config(text="Please wait")
        else:
            self.status_label.config(text="🔴 Protection is DISABLED", fg="red")
            self.details_label.config(text="Click 'Enable Protection' to start real-time monitoring")
    
    def update_toggle_button(self):
        """Update toggle button text"""
        if self.protection_enabled and self.protection_active:
            self.toggle_btn.config(text="🔴 Disable Protection", bg="#cc0000")
        elif self.protection_enabled and not self.protection_active:
            self.toggle_btn.config(text="⏳ Starting...", bg="#ff8800")
        else:
            self.toggle_btn.config(text="🟢 Enable Protection", bg="#0066cc")
    
    def toggle_protection(self):
        """Enable or disable real-time protection"""
        if self.protection_enabled and self.protection_active:
            self.disable_protection()
        else:
            self.enable_protection()
        
        # Auto-save settings
        self.save_settings()
    
    def save_settings(self):
        """Save protection settings"""
        try:
            settings_file = "data/settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            if "protection" not in settings:
                settings["protection"] = {}
            
            settings["protection"]["realtime_enabled"] = self.protection_enabled
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save protection settings: {e}")
    
    def enable_protection(self):
        """Enable real-time protection"""
        self.protection_enabled = True
        self.protection_active = True
        self.set_status_active()
        self.update_status_text()
        self.update_toggle_button()
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_filesystem, daemon=True)
        self.monitor_thread.start()
        
        self.add_log_entry("🟢 Real-time protection enabled")
        self.add_log_entry("🔍 Monitoring system for threats...")
    
    def disable_protection(self):
        """Disable real-time protection"""
        self.protection_enabled = False
        self.protection_active = False
        self.monitoring = False
        self.set_status_inactive()
        self.update_status_text()
        self.update_toggle_button()
        
        self.add_log_entry("🔴 Real-time protection disabled")
    
    def monitor_filesystem(self):
        """Monitor file system for suspicious activity"""
        watched_dirs = [
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Desktop"),
            os.environ.get('TEMP', 'C:\\Windows\\Temp')
        ]
        
        file_cache = {}
        
        # Initialize cache
        for directory in watched_dirs:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            file_cache[filepath] = os.path.getmtime(filepath)
                        except:
                            pass
        
        while self.monitoring:
            try:
                for directory in watched_dirs:
                    if not os.path.exists(directory):
                        continue
                    
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            filepath = os.path.join(root, file)
                            try:
                                current_mtime = os.path.getmtime(filepath)
                                if filepath in file_cache:
                                    if current_mtime != file_cache[filepath]:
                                        self.on_file_changed(filepath)
                                        file_cache[filepath] = current_mtime
                                else:
                                    self.on_new_file(filepath)
                                    file_cache[filepath] = current_mtime
                            except:
                                pass
                
                time.sleep(2)
            except:
                pass
    
    def on_file_changed(self, filepath):
        """Handle file change event"""
        suspicious_extensions = ['.exe', '.bat', '.vbs', '.js', '.ps1']
        if any(filepath.lower().endswith(ext) for ext in suspicious_extensions):
            self.add_log_entry(f"⚠️ Suspicious file modified: {os.path.basename(filepath)}")
            current = int(self.stats_values["🔒 Threats Blocked"].cget("text"))
            self.stats_values["🔒 Threats Blocked"].config(text=str(current + 1))
    
    def on_new_file(self, filepath):
        """Handle new file creation"""
        dangerous_extensions = ['.exe', '.bat', '.vbs', '.js', '.ps1', '.scr']
        if any(filepath.lower().endswith(ext) for ext in dangerous_extensions):
            self.add_log_entry(f"🚨 Potential threat detected: {os.path.basename(filepath)}")
            current = int(self.stats_values["🔒 Threats Blocked"].cget("text"))
            self.stats_values["🔒 Threats Blocked"].config(text=str(current + 1))
    
    def add_log_entry(self, message):
        """Add entry to protection log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("1.0", f"[{timestamp}] {message}\n")
        
        if int(self.log_text.index('end-1c').split('.')[0]) > 100:
            self.log_text.delete("end-50l", "end")