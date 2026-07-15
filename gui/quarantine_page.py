import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import json
from datetime import datetime
import sys


class QuarantineManager:
    def __init__(self):
        # Use AppData folder (safe location with permissions)
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        self.quarantine_dir = os.path.join(app_data, 'NexusAntivirus', 'quarantine')
        self.index_file = os.path.join(self.quarantine_dir, "index.json")
        self.quarantined_items = []
        self.load_index()
    
    def load_index(self):
        """Load quarantine index file."""
        try:
            os.makedirs(self.quarantine_dir, exist_ok=True)
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r') as f:
                    self.quarantined_items = json.load(f)
            else:
                self.quarantined_items = []
                self.save_index()
        except Exception as e:
            print(f"Failed to load quarantine: {e}")
            self.quarantined_items = []
    
    def save_index(self):
        """Save quarantine index file."""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.quarantined_items, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save quarantine index: {e}")
            return False
    
    def quarantine_file(self, file_path, threat_name):
        """Move file to quarantine with fallback."""
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        try:
            # Create unique name in quarantine
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_path = os.path.join(
                self.quarantine_dir,
                f"{timestamp}_{filename}"
            )
            
            # First attempt: shutil.move
            try:
                shutil.move(file_path, quarantine_path)
            except (PermissionError, OSError) as e:
                # If move fails due to permissions, try copy + delete
                try:
                    shutil.copy2(file_path, quarantine_path)
                    os.remove(file_path)
                except Exception as copy_err:
                    return False, f"Failed to quarantine: {str(copy_err)}"
            
            # Verify the file is now in quarantine
            if not os.path.exists(quarantine_path):
                return False, "Quarantine file not found after move"
            
            # Add to index
            self.quarantined_items.append({
                'original_path': file_path,
                'quarantine_path': quarantine_path,
                'threat_name': threat_name,
                'timestamp': datetime.now().isoformat(),
                'status': 'quarantined'
            })
            self.save_index()
            return True, "File quarantined successfully"
            
        except Exception as e:
            return False, f"Quarantine error: {str(e)}"
    
    def restore_file(self, item_index):
        """Restore file from quarantine."""
        try:
            item = self.quarantined_items[item_index]
            original_path = item['original_path']
            quarantine_path = item['quarantine_path']
            
            if not os.path.exists(quarantine_path):
                messagebox.showerror("Error", "Quarantined file not found!")
                return False
            
            # If original exists, create backup
            if os.path.exists(original_path):
                backup_path = original_path + ".backup"
                shutil.move(original_path, backup_path)
            
            shutil.move(quarantine_path, original_path)
            
            self.quarantined_items.pop(item_index)
            self.save_index()
            return True
        except Exception as e:
            print(f"Failed to restore: {e}")
            messagebox.showerror("Error", f"Failed to restore file: {str(e)}")
            return False
    
    def delete_permanently(self, item_index):
        """Permanently delete quarantined file."""
        try:
            item = self.quarantined_items[item_index]
            quarantine_path = item['quarantine_path']
            
            if os.path.exists(quarantine_path):
                os.remove(quarantine_path)
            
            self.quarantined_items.pop(item_index)
            self.save_index()
            return True
        except Exception as e:
            print(f"Failed to delete: {e}")
            return False
    
    def get_quarantine_location(self):
        return self.quarantine_dir