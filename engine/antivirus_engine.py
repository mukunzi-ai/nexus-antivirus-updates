# engine/antivirus_engine.py
import os
import hashlib
import re
import json

class AntivirusEngine:
    def __init__(self):
        self.signature_db = {}
        self.load_signatures()
        self.heuristic_rules = {
            'pe_imports': ['CreateRemoteThread', 'WriteProcessMemory', 'VirtualAllocEx'],
            'suspicious_strings': ['cmd.exe', 'powershell', 'wscript', 'regedit'],
            'file_extensions': ['.exe', '.dll', '.scr', '.pif', '.cmd', '.bat']
        }
    
    def load_signatures(self):
        """Load virus signatures from database file."""
        db_path = 'data/signatures.json'
        
        # Default signatures (you'll want to expand this)
        default_signatures = {
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855': 'EICAR Test Virus',
            '44d88612fea8a8f36de82e1278abb02f': 'Test.Malware.A',
            'd41d8cd98f00b204e9800998ecf8427e': 'Test.Malware.B'
        }
        
        try:
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    self.signature_db = json.load(f)
            else:
                self.signature_db = default_signatures
                os.makedirs('data', exist_ok=True)
                with open(db_path, 'w') as f:
                    json.dump(default_signatures, f, indent=2)
        except:
            self.signature_db = default_signatures
    
    def get_threat_name(self, file_hash):
        """Get threat name from hash."""
        return self.signature_db.get(file_hash, None)
    
    def scan(self, file_path):
        """Scan file for threats."""
        result = {
            "file": file_path,
            "status": "Safe",
            "score": 0,
            "reasons": []
        }
        
        try:
            # Check file size
            size = os.path.getsize(file_path)
            if size == 0:
                result["reasons"].append("Empty file")
                return result
            
            # Calculate hash
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
            
            # Signature check
            if file_hash in self.signature_db:
                result["status"] = "Infected"
                result["score"] = 100
                result["reasons"].append(f"Signature match: {self.signature_db[file_hash]}")
                return result
            
            # Heuristic analysis
            score = self.heuristic_analysis(content, file_path)
            if score > 50:
                result["status"] = "Suspicious"
                result["score"] = score
                result["reasons"].append("Heuristic detection triggered")
            elif score > 25:
                result["status"] = "Potential Risk"
                result["score"] = score
                result["reasons"].append("Suspicious patterns found")
            
            return result
            
        except Exception as e:
            result["status"] = "Error"
            result["reasons"].append(str(e))
            return result
    
    def heuristic_analysis(self, content, file_path):
        """Perform heuristic analysis on file."""
        score = 0
        
        # Convert content to string for pattern matching
        try:
            text_content = content.decode('utf-8', errors='ignore')
        except:
            text_content = ''
        
        # Check for suspicious strings
        for pattern in self.heuristic_rules['suspicious_strings']:
            if pattern in text_content.lower():
                score += 15
        
        # Check for suspicious imports (for executables)
        if file_path.lower().endswith('.exe'):
            # Look for suspicious PE imports
            for import_name in self.heuristic_rules['pe_imports']:
                if import_name in text_content:
                    score += 20
        
        # Check file entropy (encrypted/packed executables)
        if len(content) > 0:
            entropy = self.calculate_entropy(content)
            if entropy > 7.5:  # High entropy often indicates packed/encrypted files
                score += 15
        
        # Check for known malicious patterns
        malicious_patterns = [
            r'www\..*\.ru',
            r'cmd\.exe /c',
            r'reg add',
            r'wscript',
            r'CreateObject\(".*\.Shell"\)'
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, text_content, re.IGNORECASE):
                score += 10
        
        return min(score, 100)  # Cap at 100
    
    def calculate_entropy(self, data):
        """Calculate Shannon entropy of data."""
        if not data:
            return 0
        
        entropy = 0
        for i in range(256):
            count = data.count(i)
            if count > 0:
                frequency = count / len(data)
                entropy -= frequency * (frequency.bit_length())
        
        return entropy
    
    def add_signature(self, file_hash, threat_name):
        """Add new virus signature."""
        self.signature_db[file_hash] = threat_name
        
        # Save to file
        db_path = 'data/signatures.json'
        try:
            os.makedirs('data', exist_ok=True)
            with open(db_path, 'w') as f:
                json.dump(self.signature_db, f, indent=2)
            return True
        except:
            return False
