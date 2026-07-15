import tkinter as tk
import threading
import os
import sys
from PIL import Image, ImageDraw


class SystemTray:
    def __init__(self, app):
        """
        System tray icon for Nexus Antivirus
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.icon = None
        self.tray_thread = None
        self.running = False
        self.tk_root = app.root
        
        # Try to import pystray
        try:
            import pystray
            self.pystray = pystray
        except ImportError:
            print("⚠️ pystray not installed. System tray will not work.")
            print("   Install with: pip install pystray")
            self.pystray = None
    
    def create_tray_icon(self):
        """Create system tray icon"""
        if not self.pystray:
            return False
        
        # Create icon image
        image = self._create_icon_image()
        
        # Create menu
        menu = self.pystray.Menu(
            self.pystray.MenuItem("🛡️ Nexus Antivirus", self._on_icon_click),
            self.pystray.MenuItem("🔍 Quick Scan", self._on_quick_scan),
            self.pystray.MenuItem("📋 Quarantine", self._on_quarantine),
            self.pystray.MenuItem("⚙️ Settings", self._on_settings),
            self.pystray.MenuItem("📊 Dashboard", self._on_dashboard),
            self.pystray.Menu.SEPARATOR,
            self.pystray.MenuItem("🔄 Check Updates", self._on_check_updates),
            self.pystray.MenuItem("📖 About", self._on_about),
            self.pystray.Menu.SEPARATOR,
            self.pystray.MenuItem("🚪 Exit", self._on_exit)
        )
        
        # Create icon
        self.icon = self.pystray.Icon(
            "nexus_antivirus",
            image,
            "Nexus Antivirus",
            menu
        )
        
        return True
    
    def _create_icon_image(self):
        """Create a simple shield icon for tray"""
        try:
            # Create a 64x64 image
            size = 64
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw a shield shape
            # Center point
            cx, cy = size // 2, size // 2
            
            # Draw shield
            draw.rectangle(
                [cx - 20, cy - 25, cx + 20, cy + 25],
                fill=(0, 150, 255, 200),
                outline=(0, 100, 200, 255),
                width=2
            )
            
            # Draw checkmark
            draw.line(
                [cx - 10, cy, cx - 3, cy + 10],
                fill=(255, 255, 255, 255),
                width=4
            )
            draw.line(
                [cx - 3, cy + 10, cx + 12, cy - 10],
                fill=(255, 255, 255, 255),
                width=4
            )
            
            return image
            
        except Exception as e:
            print(f"Failed to create icon: {e}")
            # Create a simple colored square as fallback
            image = Image.new('RGB', (64, 64), (0, 150, 255))
            return image
    
    def show_tray(self):
        """Show the tray icon in a separate thread"""
        if not self.pystray:
            print("⚠️ System tray not available")
            return False
        
        if self.icon and self.running:
            return True
        
        if not self.create_tray_icon():
            return False
        
        self.running = True
        
        # Run icon in separate thread
        def run_icon():
            try:
                self.icon.run()
            except Exception as e:
                print(f"Tray icon error: {e}")
            finally:
                self.running = False
        
        self.tray_thread = threading.Thread(target=run_icon, daemon=True)
        self.tray_thread.start()
        
        print("✅ System tray icon created")
        return True
    
    def hide_tray(self):
        """Hide the tray icon"""
        if self.icon:
            try:
                self.icon.stop()
                self.running = False
                print("✅ System tray icon hidden")
            except:
                pass
    
    def hide_to_tray(self):
        """Hide the main window to system tray"""
        if self.tk_root:
            self.tk_root.withdraw()  # Hide window
            self.show_tray()
    
    def show_from_tray(self):
        """Show the main window from system tray"""
        if self.tk_root:
            self.tk_root.deiconify()  # Show window
            self.tk_root.lift()  # Bring to front
            self.tk_root.focus_force()
    
    def _on_icon_click(self):
        """Handle icon click"""
        if self.tk_root:
            if self.tk_root.state() == 'withdrawn':
                self.show_from_tray()
            else:
                self.tk_root.iconify()
    
    def _on_quick_scan(self):
        """Quick scan from tray"""
        self.show_from_tray()
        # Trigger quick scan
        if self.app:
            self.app.show_scanner()
            # Wait for scanner to load then start scan
            self.tk_root.after(500, lambda: self._trigger_quick_scan())
    
    def _trigger_quick_scan(self):
        """Actually trigger the quick scan"""
        try:
            # Find scanner page and start quick scan
            for child in self.tk_root.winfo_children():
                if hasattr(child, 'show_scanner'):
                    child.show_scanner()
                    # Wait for page to load
                    self.tk_root.after(200, lambda: self._find_and_scan(child))
                    break
        except:
            pass
    
    def _find_and_scan(self, frame):
        """Find scanner page and start scan"""
        try:
            for child in frame.winfo_children():
                if hasattr(child, 'quick_scan'):
                    child.quick_scan()
                    break
        except:
            pass
    
    def _on_quarantine(self):
        """Open quarantine from tray"""
        self.show_from_tray()
        if self.app:
            self.app.show_quarantine()
    
    def _on_settings(self):
        """Open settings from tray"""
        self.show_from_tray()
        if self.app:
            self.app.show_settings()
    
    def _on_dashboard(self):
        """Open dashboard from tray"""
        self.show_from_tray()
        if self.app:
            self.app.show_dashboard()
    
    def _on_check_updates(self):
        """Check for updates from tray"""
        self.show_from_tray()
        if self.app:
            self.app.show_settings()
            # Switch to updates tab
            self.tk_root.after(300, self._switch_to_updates)
    
    def _switch_to_updates(self):
        """Switch to updates tab"""
        try:
            for child in self.tk_root.winfo_children():
                if hasattr(child, 'show_settings'):
                    # Find notebook and switch to updates tab
                    for subchild in child.winfo_children():
                        if hasattr(subchild, 'select'):
                            subchild.select(4)  # Updates tab is index 4
                            # Trigger check updates
                            for grandchild in subchild.winfo_children():
                                if hasattr(grandchild, 'check_updates'):
                                    grandchild.check_updates()
                                    break
                            break
                    break
        except:
            pass
    
    def _on_about(self):
        """Show about from tray"""
        self.show_from_tray()
        if self.app:
            self.app.show_settings()
            self.tk_root.after(300, self._switch_to_about)
    
    def _switch_to_about(self):
        """Switch to about tab"""
        try:
            for child in self.tk_root.winfo_children():
                if hasattr(child, 'show_settings'):
                    for subchild in child.winfo_children():
                        if hasattr(subchild, 'select'):
                            subchild.select(5)  # About tab is index 5
                            break
                    break
        except:
            pass
    
    def _on_exit(self):
        """Exit the application from tray"""
        if self.tk_root:
            self.tk_root.quit()
            self.tk_root.destroy()