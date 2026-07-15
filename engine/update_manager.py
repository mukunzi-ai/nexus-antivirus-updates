import os
import json
import requests
import hashlib
from datetime import datetime, timedelta
import threading
import time
import shutil
import sys


class UpdateManager:
    def __init__(self):
        # Use AppData folder for updates (safe location)
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        self.update_dir = os.path.join(app_data, 'NexusAntivirus', 'updates')
        self.signatures_file = os.path.join(self.update_dir, 'signatures.json')
        self.version_file = os.path.join(self.update_dir, 'version.json')
        self.backup_dir = os.path.join(self.update_dir, 'backup')
        
        # Update server (you can change this to your own server)
        self.update_server = "https://raw.githubusercontent.com/your-repo/nexus-antivirus/main/updates/"
        
        # Current version
        self.current_version = self.get_current_version()
        
        # Create directories
        os.makedirs(self.update_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Auto-check updates every 24 hours
        self.auto_update_thread = None
        self.running = False
    
    def get_current_version(self):
        """Get current version from local file"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('version', '1.0.0')
        except:
            pass
        return '1.0.0'
    
    def get_local_signatures(self):
        """Get local signatures"""
        try:
            if os.path.exists(self.signatures_file):
                with open(self.signatures_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_local_signatures(self, signatures, version):
        """Save signatures to local file"""
        try:
            # Backup existing signatures
            if os.path.exists(self.signatures_file):
                backup_path = os.path.join(
                    self.backup_dir,
                    f"signatures_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                shutil.copy2(self.signatures_file, backup_path)
            
            # Save new signatures
            with open(self.signatures_file, 'w') as f:
                json.dump(signatures, f, indent=2)
            
            # Save version
            with open(self.version_file, 'w') as f:
                json.dump({
                    'version': version,
                    'last_update': datetime.now().isoformat(),
                    'signature_count': len(signatures)
                }, f, indent=2)
            
            self.current_version = version
            return True
        except Exception as e:
            print(f"Failed to save signatures: {e}")
            return False
    
    def check_for_updates(self):
        """Check if updates are available"""
        try:
            # Get remote version info
            response = requests.get(
                f"{self.update_server}version.json",
                timeout=10
            )
            
            if response.status_code == 200:
                remote_data = response.json()
                remote_version = remote_data.get('version', '0.0.0')
                
                # Compare versions
                if self._compare_versions(remote_version, self.current_version) > 0:
                    return {
                        'available': True,
                        'version': remote_version,
                        'signature_count': remote_data.get('signature_count', 0),
                        'changelog': remote_data.get('changelog', '')
                    }
            
            return {'available': False}
            
        except Exception as e:
            print(f"Update check failed: {e}")
            return {'available': False, 'error': str(e)}
    
    def download_updates(self, callback=None):
        """Download and apply updates"""
        try:
            if callback:
                callback('Checking for updates...', 0)
            
            # Get remote version info
            response = requests.get(
                f"{self.update_server}version.json",
                timeout=10
            )
            
            if response.status_code != 200:
                if callback:
                    callback('Failed to connect to update server', 100)
                return False, 'Failed to connect to update server'
            
            remote_data = response.json()
            remote_version = remote_data.get('version', '0.0.0')
            
            if callback:
                callback(f'New version {remote_version} found!', 20)
            
            # Download signatures
            if callback:
                callback('Downloading signatures...', 40)
            
            sig_response = requests.get(
                f"{self.update_server}signatures.json",
                timeout=30
            )
            
            if sig_response.status_code != 200:
                if callback:
                    callback('Failed to download signatures', 100)
                return False, 'Failed to download signatures'
            
            new_signatures = sig_response.json()
            
            # Download changelog (optional)
            if callback:
                callback('Applying updates...', 70)
            
            # Save signatures
            if self.save_local_signatures(new_signatures, remote_version):
                if callback:
                    callback('Update complete!', 100)
                return True, 'Update successful'
            else:
                if callback:
                    callback('Failed to save signatures', 100)
                return False, 'Failed to save signatures'
                
        except Exception as e:
            if callback:
                callback(f'Error: {str(e)}', 100)
            return False, f'Error: {str(e)}'
    
    def auto_update_check(self, callback=None):
        """Automatically check for updates in background"""
        if self.running:
            return
        
        self.running = True
        self.auto_update_thread = threading.Thread(
            target=self._auto_update_loop,
            args=(callback,),
            daemon=True
        )
        self.auto_update_thread.start()
    
    def _auto_update_loop(self, callback=None):
        """Background update loop"""
        while self.running:
            try:
                # Check for updates every 24 hours
                time.sleep(24 * 60 * 60)  # 24 hours
                
                if callback:
                    callback('Checking for updates...')
                
                result = self.check_for_updates()
                
                if result.get('available', False):
                    if callback:
                        callback(f'Update available: v{result["version"]}')
                    
                    # Auto-download update
                    success, message = self.download_updates(callback)
                    
                    if callback:
                        if success:
                            callback('✅ Auto-update successful!')
                        else:
                            callback(f'❌ Auto-update failed: {message}')
                
            except Exception as e:
                if callback:
                    callback(f'Auto-update error: {str(e)}')
    
    def stop_auto_update(self):
        """Stop auto-update thread"""
        self.running = False
        if self.auto_update_thread:
            self.auto_update_thread.join(timeout=2)
    
    def _compare_versions(self, v1, v2):
        """Compare version strings"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_val = v1_parts[i] if i < len(v1_parts) else 0
            v2_val = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1_val > v2_val:
                return 1
            elif v1_val < v2_val:
                return -1
        
        return 0
    
    def get_last_update_time(self):
        """Get last update time"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('last_update', 'Never')
        except:
            pass
        return 'Never'
    
    def get_signature_count(self):
        """Get number of signatures"""
        signatures = self.get_local_signatures()
        return len(signatures)
    
    def rollback_update(self):
        """Rollback to previous version"""
        try:
            # Find latest backup
            backup_files = [f for f in os.listdir(self.backup_dir) if f.startswith('signatures_backup_')]
            if not backup_files:
                return False, 'No backup found'
            
            # Sort by timestamp (newest first)
            backup_files.sort(reverse=True)
            latest_backup = os.path.join(self.backup_dir, backup_files[0])
            
            # Restore backup
            shutil.copy2(latest_backup, self.signatures_file)
            
            return True, 'Rollback successful'
        except Exception as e:
            return False, f'Rollback failed: {str(e)}'
    
    def get_update_status(self):
        """Get current update status"""
        return {
            'current_version': self.current_version,
            'last_update': self.get_last_update_time(),
            'signature_count': self.get_signature_count(),
            'auto_update_enabled': self.running,
            'update_dir': self.update_dir
        }


# Function to add initial signatures (for testing)
def create_initial_signatures():
    """Create initial signatures database"""
    initial_signatures = {
        # EICAR test virus (safe for testing)
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855': {
            'name': 'EICAR Test Virus',
            'severity': 'Test',
            'type': 'Test File'
        },
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
        # Common malware hashes (examples)
        '4a09a8a1c8afc5e0f7b7f5e8d8f0a7f4': {
            'name': 'Trojan.Generic.A',
            'severity': 'High',
            'type': 'Trojan'
        },
        'f5a0a8d4a7f5a4b8c6a7f4b8c6a7f4b8': {
            'name': 'Worm.Agent.B',
            'severity': 'High',
            'type': 'Worm'
        },
        'b7f5e8d8f0a7f4a09a8a1c8afc5e0f7b': {
            'name': 'Ransomware.Wannacry',
            'severity': 'Critical',
            'type': 'Ransomware'
        },
        'c6a7f4b8a09a8a1c8afc5e0f7b7f5e8d': {
            'name': 'Backdoor.Agent.C',
            'severity': 'High',
            'type': 'Backdoor'
        }
    }
    
    app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
    update_dir = os.path.join(app_data, 'NexusAntivirus', 'updates')
    signatures_file = os.path.join(update_dir, 'signatures.json')
    version_file = os.path.join(update_dir, 'version.json')
    
    os.makedirs(update_dir, exist_ok=True)
    
    with open(signatures_file, 'w') as f:
        json.dump(initial_signatures, f, indent=2)
    
    with open(version_file, 'w') as f:
        json.dump({
            'version': '1.0.0',
            'last_update': datetime.now().isoformat(),
            'signature_count': len(initial_signatures)
        }, f, indent=2)
    
    print(f"✅ Initial signatures created at: {signatures_file}")
    print(f"   {len(initial_signatures)} signatures added")