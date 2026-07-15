import threading
import time
import json
import os
from datetime import datetime, timedelta
from scanner.fast_scanner import FastScanner


class ScanScheduler:
    def __init__(self, callback=None):
        self.schedule_file = "data/schedule.json"
        self.scheduler_thread = None
        self.running = False
        self.callback = callback
        self.scanner = FastScanner(max_workers=4)
        self.schedule = self.load_schedule()
        
    def load_schedule(self):
        """Load schedule from file"""
        default_schedule = {
            "quick_scan": {
                "enabled": False,
                "frequency": "daily",
                "time": "02:00",
                "last_run": None
            },
            "full_scan": {
                "enabled": False,
                "frequency": "weekly",
                "time": "03:00",
                "day": "Sunday",
                "last_run": None
            }
        }
        
        try:
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, 'r') as f:
                    return json.load(f)
            else:
                os.makedirs("data", exist_ok=True)
                with open(self.schedule_file, 'w') as f:
                    json.dump(default_schedule, f, indent=2)
                return default_schedule
        except:
            return default_schedule
    
    def save_schedule(self):
        """Save schedule to file"""
        try:
            with open(self.schedule_file, 'w') as f:
                json.dump(self.schedule, f, indent=2)
            return True
        except:
            return False
    
    def update_schedule(self, scan_type, enabled, frequency=None, time=None, day=None):
        """Update schedule settings"""
        if scan_type in self.schedule:
            self.schedule[scan_type]["enabled"] = enabled
            if frequency:
                self.schedule[scan_type]["frequency"] = frequency
            if time:
                self.schedule[scan_type]["time"] = time
            if day:
                self.schedule[scan_type]["day"] = day
            self.save_schedule()
            return True
        return False
    
    def start_scheduler(self):
        """Start the scheduler in background"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self.scheduler_thread.start()
        print("✅ Scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
        print("⏹️ Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check quick scan schedule
                if self.schedule["quick_scan"]["enabled"]:
                    self._check_quick_scan(current_time)
                
                # Check full scan schedule
                if self.schedule["full_scan"]["enabled"]:
                    self._check_full_scan(current_time)
                
                # Sleep for 60 seconds before checking again
                time.sleep(60)
                
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _check_quick_scan(self, current_time):
        """Check if quick scan should run"""
        schedule = self.schedule["quick_scan"]
        scan_time = schedule["time"]
        
        try:
            hour, minute = map(int, scan_time.split(':'))
            scheduled_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Check if it's time to run
            if abs((current_time - scheduled_time).total_seconds()) < 60:
                # Check if already ran today
                if schedule.get("last_run"):
                    last_run = datetime.fromisoformat(schedule["last_run"])
                    if schedule["frequency"] == "daily":
                        if last_run.date() == current_time.date():
                            return
                    elif schedule["frequency"] == "weekly":
                        if last_run.isocalendar()[1] == current_time.isocalendar()[1]:
                            return
                
                # Run the scan
                self._run_scan("Quick Scan", self.scanner.scan_system_fast)
                schedule["last_run"] = current_time.isoformat()
                self.save_schedule()
                
        except Exception as e:
            print(f"Quick scan check error: {e}")
    
    def _check_full_scan(self, current_time):
        """Check if full scan should run"""
        schedule = self.schedule["full_scan"]
        scan_time = schedule["time"]
        scan_day = schedule.get("day", "Sunday")
        
        try:
            hour, minute = map(int, scan_time.split(':'))
            scheduled_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Check if it's time to run
            if abs((current_time - scheduled_time).total_seconds()) < 60:
                # Check if correct day
                current_day = current_time.strftime("%A")
                if current_day != scan_day:
                    return
                
                # Check if already ran this week
                if schedule.get("last_run"):
                    last_run = datetime.fromisoformat(schedule["last_run"])
                    if last_run.isocalendar()[1] == current_time.isocalendar()[1]:
                        return
                
                # Run the scan
                self._run_scan("Full Scan", self.scanner.scan_full_system_fast)
                schedule["last_run"] = current_time.isoformat()
                self.save_schedule()
                
        except Exception as e:
            print(f"Full scan check error: {e}")
    
    def _run_scan(self, scan_name, scan_func):
        """Execute a scheduled scan"""
        def scan_thread():
            print(f"🔄 Starting scheduled {scan_name} at {datetime.now()}")
            
            if self.callback:
                self.callback(f"🔄 Scheduled {scan_name} started...", "info")
            
            try:
                # Run the scan
                results = scan_func()
                
                threat_count = len([r for r in results if r.get('status') != 'Safe'])
                
                message = f"✅ {scan_name} complete: {len(results)} files, {threat_count} threats found"
                print(message)
                
                if self.callback:
                    if threat_count > 0:
                        self.callback(f"⚠️ {message}", "warning")
                    else:
                        self.callback(f"✅ {message}", "success")
                        
            except Exception as e:
                error_msg = f"❌ Scheduled {scan_name} failed: {str(e)}"
                print(error_msg)
                if self.callback:
                    self.callback(error_msg, "error")
        
        # Run in separate thread
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
    
    def get_next_run_time(self, scan_type):
        """Get next scheduled run time"""
        if scan_type not in self.schedule:
            return None
        
        schedule = self.schedule[scan_type]
        if not schedule["enabled"]:
            return None
        
        try:
            current_time = datetime.now()
            hour, minute = map(int, schedule["time"].split(':'))
            
            if scan_type == "quick_scan":
                scheduled_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                if scheduled_time < current_time:
                    if schedule["frequency"] == "daily":
                        scheduled_time += timedelta(days=1)
                    elif schedule["frequency"] == "weekly":
                        scheduled_time += timedelta(days=7)
                
                return scheduled_time
                
            elif scan_type == "full_scan":
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                target_day = days.index(schedule.get("day", "Sunday"))
                current_day = current_time.weekday()
                
                days_until = target_day - current_day
                if days_until <= 0:
                    days_until += 7
                
                scheduled_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                scheduled_time += timedelta(days=days_until)
                
                return scheduled_time
                
        except:
            pass
        
        return None