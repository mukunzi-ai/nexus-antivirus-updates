# scanner/scanner.py
import os
import hashlib
import threading
import time
from datetime import datetime
from pathlib import Path
from engine.antivirus_engine import AntivirusEngine

class Scanner:
    def __init__(self):
        self.engine = AntivirusEngine()
        self.threats = []
        self.scanned_count = 0
        self.total_files = 0
        self.scanning = False
        self.current_file = ""
        self.start_time = None
        self.elapsed_time = 0
        
    def calculate_hash(self, file_path):
        """Calculate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as file:
                while True:
                    data = file.read(4096)
                    if not data:
                        break
                    sha256.update(data)
            return sha256.hexdigest()
        except Exception:
            return None
    
    def get_file_extension(self, file_path):
        """Get file extension for filtering."""
        return Path(file_path).suffix.lower()
    
    def should_scan_file(self, file_path):
        """Determine if file should be scanned based on extension."""
        # Skip system files and very large files
        extensions_to_scan = {
            '.exe', '.dll', '.sys', '.msi', '.com', '.bat', '.cmd',
            '.js', '.vbs', '.ps1', '.sh', '.py', '.jar', '.apk',
            '.doc', '.docx', '.xls', '.xlsx', '.pdf', '.zip', '.rar'
        }
        
        ext = self.get_file_extension(file_path)
        
        # Skip if file is too large (>100MB)
        try:
            if os.path.getsize(file_path) > 100 * 1024 * 1024:
                return False
        except:
            return False
            
        return ext in extensions_to_scan or ext == ''  # Scan files without extension too
    
    def scan_file(self, file_path, callback=None):
        """Scan a single file with callback support."""
        if not os.path.isfile(file_path):
            result = {
                "file": file_path,
                "status": "Error",
                "score": 0,
                "reasons": ["File not found"],
                "hash": None,
                "timestamp": datetime.now().isoformat()
            }
            if callback:
                callback(result)
            return result
        
        self.current_file = file_path
        self.scanned_count += 1
        
        file_hash = self.calculate_hash(file_path)
        result = self.engine.scan(file_path)
        result["hash"] = file_hash
        result["timestamp"] = datetime.now().isoformat()
        
        if result["status"] != "Safe":
            result["threat_name"] = self.engine.get_threat_name(file_hash) or "Unknown Threat"
            self.threats.append(result)
        
        if callback:
            callback(result)
            
        return result
    
    def scan_folder(self, folder_path, callback=None):
        """Scan an entire folder with progress updates."""
        results = []
        self.threats = []
        self.scanned_count = 0
        self.total_files = 0
        self.scanning = True
        self.start_time = time.time()
        
        if not os.path.isdir(folder_path):
            self.scanning = False
            return results
        
        # First, count total files
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                full_path = os.path.join(root, filename)
                if self.should_scan_file(full_path):
                    self.total_files += 1
        
        # Now scan
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if not self.scanning:
                    break
                full_path = os.path.join(root, filename)
                if self.should_scan_file(full_path):
                    try:
                        result = self.scan_file(full_path, callback)
                        results.append(result)
                    except Exception as e:
                        error_result = {
                            "file": full_path,
                            "status": "Error",
                            "score": 0,
                            "reasons": [str(e)],
                            "hash": None,
                            "timestamp": datetime.now().isoformat()
                        }
                        results.append(error_result)
                        if callback:
                            callback(error_result)
            if not self.scanning:
                break
        
        self.scanning = False
        self.elapsed_time = time.time() - self.start_time
        return results
    
    def scan_system(self, callback=None):
        """Quick scan of common system locations."""
        scan_paths = [
            os.environ.get('TEMP', 'C:\\Windows\\Temp'),
            os.path.expanduser('~\\Downloads'),
            os.path.expanduser('~\\Desktop'),
            'C:\\Windows\\System32\\drivers' if os.name == 'nt' else '/etc',
        ]
        
        all_results = []
        for path in scan_paths:
            if os.path.exists(path):
                results = self.scan_folder(path, callback)
                all_results.extend(results)
        
        return all_results
    
    def scan_critical_areas(self, callback=None):
        """Scan critical system areas."""
        critical_paths = [
            'C:\\Windows\\System32' if os.name == 'nt' else '/usr/bin',
            'C:\\Windows\\SysWOW64' if os.name == 'nt' else '/usr/local/bin',
            os.path.expanduser('~\\AppData\\Roaming') if os.name == 'nt' else '/home',
            'C:\\Program Files' if os.name == 'nt' else '/opt',
            'C:\\Program Files (x86)' if os.name == 'nt' else '/var/log',
        ]
        
        all_results = []
        for path in critical_paths:
            if os.path.exists(path):
                results = self.scan_folder(path, callback)
                all_results.extend(results)
        
        return all_results
    
    def stop_scan(self):
        """Stop ongoing scan."""
        self.scanning = False
    
    def get_scan_stats(self):
        """Get current scan statistics."""
        return {
            'scanned': self.scanned_count,
            'total': self.total_files,
            'threats': len(self.threats),
            'current_file': self.current_file,
            'elapsed_time': self.elapsed_time,
            'is_scanning': self.scanning
        }
    
    def get_threats(self):
        return self.threats
    
    def clear_threats(self):
        self.threats.clear()
        self.scanned_count = 0
        self.total_files = 0