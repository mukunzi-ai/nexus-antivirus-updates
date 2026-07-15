import os
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import re
import zipfile
import tarfile
import gzip
import tempfile
import shutil
from pathlib import Path


class FastScanner:
    def __init__(self, max_workers=8):
        """
        Ultra-fast multi-threaded scanner with advanced features
        
        Args:
            max_workers: Number of threads (default: 8 for SSDs)
        """
        self.max_workers = max_workers
        self.scan_results = []
        self.threats_found = []
        self.scanned_count = 0
        self.total_files = 0
        self.scanning = False
        self.current_file = ""
        self.start_time = None
        self.elapsed_time = 0
        self.lock = threading.Lock()
        self.quarantine_dir = "quarantine"
        self.signature_db = self.load_signatures()
        
        # File size limits (in bytes)
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_archive_size = 500 * 1024 * 1024  # 500MB
        
        # Suspicious patterns for heuristic detection
        self.suspicious_patterns = [
            (r'cmd\.exe /c', 15, 'Command execution'),
            (r'powershell -', 15, 'PowerShell execution'),
            (r'wscript', 10, 'WScript execution'),
            (r'cscript', 10, 'CScript execution'),
            (r'reg add.*HKEY', 20, 'Registry modification'),
            (r'rundll32\.exe', 10, 'Rundll32 execution'),
            (r'CreateObject\(.*Shell', 15, 'Shell object creation'),
            (r'http://', 5, 'URL in file'),
            (r'https://', 5, 'URL in file'),
            (r'\.onion', 10, 'Tor onion address'),
            (r'bitcoin', 10, 'Bitcoin reference'),
            (r'cryptocurrency', 10, 'Cryptocurrency reference'),
            (r'ransom', 20, 'Ransomware keyword'),
            (r'encrypt', 10, 'Encryption keyword'),
            (r'decrypt', 10, 'Decryption keyword'),
            (r'malware', 10, 'Malware keyword'),
            (r'virus', 10, 'Virus keyword'),
        ]
        
        # File extensions to always scan
        self.scan_extensions = {
            '.exe', '.dll', '.sys', '.msi', '.com', '.bat', '.cmd',
            '.js', '.vbs', '.ps1', '.sh', '.py', '.jar', '.apk',
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.zip', '.rar', '.7z', '.gz', '.tar', '.bz2',
            '.cab', '.msc', '.scr', '.pif', '.reg', '.inf',
            '.xml', '.html', '.htm', '.php', '.asp', '.aspx',
            '.jsp', '.cfm', '.rb', '.pl', '.pm', '.tcl', '.lua',
            '.swf', '.flv', '.mp4', '.avi', '.mkv', '.mov',
            '.wmv', '.flac', '.mp3', '.wav', '.aac', '.ogg'
        }
    
    def load_signatures(self):
        """Load virus signatures from database"""
        db_path = 'data/signatures.json'
        default_signatures = {
            # EICAR test virus (safe for testing)
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855': {
                'name': 'EICAR Test Virus',
                'severity': 'Test',
                'type': 'Test File'
            },
            # Common malware hashes (examples - you'd add real ones)
            '44d88612fea8a8f36de82e1278abb02f': {
                'name': 'Test.Malware.A',
                'severity': 'High',
                'type': 'Trojan'
            },
            'd41d8cd98f00b204e9800998ecf8427e': {
                'name': 'Test.Malware.B',
                'severity': 'Medium',
                'type': 'Worm'
            },
        }
        
        try:
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    return json.load(f)
            else:
                os.makedirs('data', exist_ok=True)
                with open(db_path, 'w') as f:
                    json.dump(default_signatures, f, indent=2)
                return default_signatures
        except:
            return default_signatures
    
    def calculate_hash(self, filepath):
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return None
    
    def calculate_md5(self, filepath):
        """Calculate MD5 hash of file"""
        md5 = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except:
            return None
    
    def calculate_entropy(self, data):
        """Calculate Shannon entropy for file content"""
        if not data:
            return 0
        try:
            entropy = 0
            for i in range(256):
                count = data.count(i)
                if count > 0:
                    frequency = count / len(data)
                    entropy -= frequency * (frequency.bit_length())
            return entropy
        except:
            return 0
    
    def should_scan_file(self, filepath):
        """Determine if file should be scanned"""
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                return False
            
            # Check file size
            size = os.path.getsize(filepath)
            if size > self.max_file_size:
                return False
            if size == 0:
                return False
            
            # Check if it's a directory
            if os.path.isdir(filepath):
                return False
            
            # Check file extension
            ext = os.path.splitext(filepath)[1].lower()
            
            # Always scan files with no extension (often dangerous)
            if ext == '':
                return True
            
            # Check against scan extensions
            return ext in self.scan_extensions
            
        except:
            return False
    
    def scan_archive(self, filepath, callback=None):
        """Extract and scan archive files"""
        results = []
        temp_dir = None
        
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            
            # Extract based on extension
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.zip':
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            elif ext == '.tar' or ext == '.tar.gz' or ext == '.tgz':
                with tarfile.open(filepath, 'r') as tar_ref:
                    tar_ref.extractall(temp_dir)
            elif ext == '.gz':
                with gzip.open(filepath, 'rb') as gz_ref:
                    out_file = os.path.join(temp_dir, os.path.basename(filepath)[:-3])
                    with open(out_file, 'wb') as f:
                        f.write(gz_ref.read())
            
            # Scan extracted files
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    extracted_path = os.path.join(root, file)
                    if self.should_scan_file(extracted_path):
                        result = self.scan_file_worker(extracted_path)
                        results.append(result)
                        if callback:
                            callback(result)
            
            return results
            
        except Exception as e:
            return [{
                'file': filepath,
                'status': 'Error',
                'score': 0,
                'reasons': [f'Archive scan failed: {str(e)}'],
                'hash': None,
                'timestamp': datetime.now().isoformat()
            }]
        finally:
            # Clean up temp directory
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def scan_file_worker(self, filepath):
        """Scan a single file - worker for thread pool"""
        self.current_file = filepath
        result = {
            'file': filepath,
            'status': 'Safe',
            'score': 0,
            'reasons': [],
            'hash': None,
            'md5': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Calculate hashes
            file_hash = self.calculate_hash(filepath)
            file_md5 = self.calculate_md5(filepath)
            result['hash'] = file_hash
            result['md5'] = file_md5
            
            # Check signature database
            if file_hash in self.signature_db:
                sig = self.signature_db[file_hash]
                result['status'] = 'Infected'
                result['score'] = 100
                result['threat_name'] = sig['name']
                result['severity'] = sig['severity']
                result['threat_type'] = sig['type']
                result['reasons'].append(f'Signature match: {sig["name"]}')
                return result
            
            # Read file content for heuristic analysis
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Calculate entropy
            entropy = self.calculate_entropy(content)
            if entropy > 7.5:
                result['score'] += 15
                result['reasons'].append(f'High entropy: {entropy:.2f} (packed/encrypted)')
            
            # Heuristic pattern matching
            try:
                text_content = content.decode('utf-8', errors='ignore')
                for pattern, score, desc in self.suspicious_patterns:
                    if re.search(pattern, text_content, re.IGNORECASE):
                        result['score'] += score
                        result['reasons'].append(f'Pattern match: {desc}')
            except:
                pass
            
            # Determine status based on score
            if result['score'] >= 70:
                result['status'] = 'Infected'
                result['threat_name'] = 'Heuristic.Malware'
                result['severity'] = 'High'
                result['threat_type'] = 'Heuristic Detection'
            elif result['score'] >= 40:
                result['status'] = 'Suspicious'
                result['threat_name'] = 'Heuristic.Suspicious'
                result['severity'] = 'Medium'
                result['threat_type'] = 'Suspicious Behavior'
            elif result['score'] >= 20:
                result['status'] = 'Potential Risk'
                result['threat_name'] = 'Heuristic.Potential'
                result['severity'] = 'Low'
                result['threat_type'] = 'Potential Risk'
            
            return result
            
        except Exception as e:
            result['status'] = 'Error'
            result['reasons'].append(str(e))
            return result
    
    def scan_folder_fast(self, folder_path, callback=None):
        """Multi-threaded folder scanning"""
        self.scan_results = []
        self.threats_found = []
        self.scanned_count = 0
        self.total_files = 0
        self.scanning = True
        self.start_time = datetime.now()
        
        if not os.path.isdir(folder_path):
            self.scanning = False
            return []
        
        # Collect all files
        files_to_scan = []
        archive_files = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                ext = os.path.splitext(filepath)[1].lower()
                
                # Check for archive files
                if ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
                    if os.path.getsize(filepath) <= self.max_archive_size:
                        archive_files.append(filepath)
                elif self.should_scan_file(filepath):
                    files_to_scan.append(filepath)
        
        self.total_files = len(files_to_scan) + len(archive_files)
        
        # Scan regular files with thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.scan_file_worker, filepath): filepath
                for filepath in files_to_scan
            }
            
            for future in as_completed(future_to_file):
                if not self.scanning:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                try:
                    result = future.result(timeout=60)
                    with self.lock:
                        self.scan_results.append(result)
                        self.scanned_count += 1
                        if result['status'] not in ['Safe', 'Clean']:
                            self.threats_found.append(result)
                    if callback:
                        callback(result)
                except Exception as e:
                    error_result = {
                        'file': future_to_file[future],
                        'status': 'Error',
                        'score': 0,
                        'reasons': [str(e)],
                        'hash': None,
                        'timestamp': datetime.now().isoformat()
                    }
                    with self.lock:
                        self.scan_results.append(error_result)
                        self.scanned_count += 1
                    if callback:
                        callback(error_result)
        
        # Scan archive files (single-threaded for safety)
        for archive in archive_files:
            if not self.scanning:
                break
            with self.lock:
                self.total_files += 1
            results = self.scan_archive(archive, callback)
            with self.lock:
                self.scan_results.extend(results)
                self.scanned_count += len(results)
                for result in results:
                    if result['status'] not in ['Safe', 'Clean']:
                        self.threats_found.append(result)
        
        self.scanning = False
        self.elapsed_time = (datetime.now() - self.start_time).total_seconds()
        return self.scan_results
    
    def scan_system_fast(self, callback=None):
        """Quick scan - most vulnerable areas"""
        scan_paths = [
            os.environ.get('TEMP', 'C:\\Windows\\Temp'),
            os.path.expanduser('~\\Downloads'),
            os.path.expanduser('~\\Desktop'),
            os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Recent'),
            os.path.expanduser('~\\AppData\\Local\\Temp'),
        ]
        
        # Add Windows temp if on Windows
        if os.name == 'nt':
            scan_paths.append('C:\\Windows\\Prefetch')
            scan_paths.append('C:\\Users\\Public\\Desktop')
        
        all_results = []
        for path in scan_paths:
            if os.path.exists(path):
                results = self.scan_folder_fast(path, callback)
                all_results.extend(results)
                if not self.scanning:
                    break
        
        return all_results
    
    def scan_full_system_fast(self, callback=None):
        """Full system scan - all critical areas"""
        critical_paths = [
            'C:\\Windows\\System32' if os.name == 'nt' else '/usr/bin',
            'C:\\Windows\\SysWOW64' if os.name == 'nt' else '/usr/local/bin',
            os.path.expanduser('~\\AppData\\Roaming') if os.name == 'nt' else '/home',
            'C:\\Program Files' if os.name == 'nt' else '/opt',
            'C:\\Program Files (x86)' if os.name == 'nt' else '/var/log',
            os.path.expanduser('~\\Documents') if os.name == 'nt' else '/var/www',
            os.path.expanduser('~\\Desktop'),
            os.path.expanduser('~\\Downloads'),
            'C:\\' if os.name == 'nt' else '/',
        ]
        
        all_results = []
        for path in critical_paths:
            if os.path.exists(path):
                results = self.scan_folder_fast(path, callback)
                all_results.extend(results)
                if not self.scanning:
                    break
        
        return all_results
    
    def scan_memory(self, callback=None):
        """Memory scan (simplified version)"""
        # This is a placeholder - real memory scanning requires system-level access
        results = []
        
        # Check running processes
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    exe_path = proc.info['exe']
                    if exe_path and os.path.exists(exe_path):
                        result = self.scan_file_worker(exe_path)
                        results.append(result)
                        if callback:
                            callback(result)
                except:
                    pass
        except ImportError:
            # Fallback if psutil not installed
            results.append({
                'file': 'Memory Scan',
                'status': 'Info',
                'score': 0,
                'reasons': ['Install psutil for memory scanning: pip install psutil'],
                'hash': None,
                'timestamp': datetime.now().isoformat()
            })
        
        return results
    
    def stop_scan(self):
        """Stop ongoing scan"""
        self.scanning = False
    
    def get_stats(self):
        """Get current scan statistics"""
        return {
            'scanned': self.scanned_count,
            'total': self.total_files,
            'threats': len(self.threats_found),
            'current_file': self.current_file,
            'elapsed_time': self.elapsed_time,
            'is_scanning': self.scanning
        }
    
    def get_threats(self):
        """Get list of detected threats"""
        return self.threats_found
    
    def clear_threats(self):
        """Clear threat list"""
        self.threats_found = []
        self.scan_results = []
    
    def quarantine_file(self, filepath, threat_name):
        """Move file to quarantine"""
        try:
            os.makedirs(self.quarantine_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(filepath)
            quarantine_path = os.path.join(
                self.quarantine_dir,
                f"{timestamp}_{filename}"
            )
            shutil.move(filepath, quarantine_path)
            
            # Save to index
            index_file = os.path.join(self.quarantine_dir, "index.json")
            try:
                with open(index_file, 'r') as f:
                    index = json.load(f)
            except:
                index = []
            
            index.append({
                'original_path': filepath,
                'quarantine_path': quarantine_path,
                'threat_name': threat_name,
                'timestamp': datetime.now().isoformat()
            })
            
            with open(index_file, 'w') as f:
                json.dump(index, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Quarantine error: {e}")
            return False