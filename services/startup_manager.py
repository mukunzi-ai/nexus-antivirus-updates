import os
import sys
import winreg
import shutil
from pathlib import Path


class StartupManager:
    def __init__(self):
        self.app_name = "NexusAntivirus"
        self.app_path = os.path.abspath(sys.argv[0])
        self.startup_folder = os.path.join(
            os.environ.get('APPDATA', ''),
            'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
        )
        self.batch_file = os.path.join(self.startup_folder, f"{self.app_name}.bat")
        
    def add_to_startup(self):
        """Add app to Windows startup (multiple methods)"""
        success = []
        
        # Method 1: Registry (most reliable)
        try:
            self._add_to_registry()
            success.append("Registry")
        except Exception as e:
            print(f"Registry startup failed: {e}")
        
        # Method 2: Startup folder
        try:
            self._add_to_startup_folder()
            success.append("Startup Folder")
        except Exception as e:
            print(f"Startup folder failed: {e}")
        
        return success
    
    def _add_to_registry(self):
        """Add to Windows registry for startup"""
        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Set value
            winreg.SetValueEx(
                key,
                self.app_name,
                0,
                winreg.REG_SZ,
                f'"{sys.executable}" "{self.app_path}" --minimized'
            )
            
            winreg.CloseKey(key)
            print("✅ Added to Windows Registry startup")
            return True
            
        except Exception as e:
            print(f"Registry add failed: {e}")
            return False
    
    def _add_to_startup_folder(self):
        """Add shortcut to Startup folder"""
        try:
            # Create batch file
            with open(self.batch_file, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'start "" "{self.app_path}" --minimized\n')
                f.write('exit\n')
            
            print(f"✅ Added to Startup folder: {self.batch_file}")
            return True
            
        except Exception as e:
            print(f"Startup folder add failed: {e}")
            return False
    
    def remove_from_startup(self):
        """Remove app from Windows startup"""
        success = []
        
        # Remove from registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, self.app_name)
                success.append("Registry")
                print("✅ Removed from Windows Registry")
            except FileNotFoundError:
                pass
            
            winreg.CloseKey(key)
            
        except Exception as e:
            print(f"Registry remove failed: {e}")
        
        # Remove from startup folder
        try:
            if os.path.exists(self.batch_file):
                os.remove(self.batch_file)
                success.append("Startup Folder")
                print("✅ Removed from Startup folder")
        except Exception as e:
            print(f"Startup folder remove failed: {e}")
        
        return success
    
    def is_in_startup(self):
        """Check if app is in startup"""
        # Check registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, self.app_name)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                pass
            
            winreg.CloseKey(key)
            
        except:
            pass
        
        # Check startup folder
        if os.path.exists(self.batch_file):
            return True
        
        return False
    
    def get_startup_methods(self):
        """Get list of startup methods currently used"""
        methods = []
        
        # Check registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            
            try:
                winreg.QueryValueEx(key, self.app_name)
                methods.append("Registry")
            except:
                pass
            
            winreg.CloseKey(key)
            
        except:
            pass
        
        # Check startup folder
        if os.path.exists(self.batch_file):
            methods.append("Startup Folder")
        
        return methods