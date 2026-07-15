import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from datetime import datetime
from scanner.fast_scanner import FastScanner
from database.db_manager import DatabaseManager
import os


class ScannerPage:
    def __init__(self, parent):
        self.scanner = FastScanner(max_workers=8)
        self.scanning = False
        self.scan_thread = None
        self.last_count = 0
        self.last_time = datetime.now()
        
        # Initialize database
        try:
            self.db = DatabaseManager()
        except:
            self.db = None
        
        self.frame = tk.Frame(parent, bg="#1a1a1a")
        
        # Title
        title = tk.Label(
            self.frame,
            text="🛡️ Advanced Virus Scanner",
            bg="#1a1a1a",
            fg="cyan",
            font=("Segoe UI", 26, "bold")
        )
        title.pack(pady=20)
        
        # Info Frame
        info_frame = tk.Frame(self.frame, bg="#1a1a1a")
        info_frame.pack(pady=5)
        
        tk.Label(
            info_frame,
            text=f"⚡ Multi-Threaded: {self.scanner.max_workers} threads | 🎯 Archive Scanning Enabled",
            bg="#1a1a1a",
            fg="#00ff88",
            font=("Segoe UI", 11)
        ).pack()
        
        # Scan Type Frame
        scan_frame = tk.Frame(self.frame, bg="#1a1a1a")
        scan_frame.pack(pady=10)
        
        scan_buttons = [
            ("⚡ Quick Scan", self.quick_scan, "#0066cc"),
            ("🔍 Full System", self.full_scan, "#cc6600"),
            ("📁 Custom", self.custom_scan, "#339933"),
            ("🧠 Memory Scan", self.memory_scan, "#9933cc"),
        ]
        
        for text, command, color in scan_buttons:
            btn = tk.Button(
                scan_frame,
                text=text,
                command=command,
                width=18,
                height=2,
                bg=color,
                fg="white",
                activebackground="#00aaaa",
                activeforeground="white",
                font=("Segoe UI", 11, "bold"),
                cursor="hand2"
            )
            btn.pack(side="left", padx=5)
        
        # Status Frame
        status_frame = tk.Frame(self.frame, bg="#1a1a1a")
        status_frame.pack(pady=15, fill="x", padx=50)
        
        # Progress Bar
        self.progress = ttk.Progressbar(
            status_frame,
            length=500,
            mode='determinate'
        )
        self.progress.pack(pady=10)
        
        # Status Labels
        self.status_label = tk.Label(
            status_frame,
            text="🟢 Ready to scan",
            bg="#1a1a1a",
            fg="lime",
            font=("Segoe UI", 12, "bold")
        )
        self.status_label.pack()
        
        self.file_label = tk.Label(
            status_frame,
            text="",
            bg="#1a1a1a",
            fg="gray",
            font=("Segoe UI", 10)
        )
        self.file_label.pack()
        
        # Stats Frame
        stats_frame = tk.Frame(self.frame, bg="#1a1a1a")
        stats_frame.pack(pady=15, fill="x", padx=50)
        
        self.stats_labels = {}
        stats = [
            ("📁 Scanned", "0"),
            ("⚠️ Threats", "0"),
            ("⏱️ Time", "00:00"),
            ("📊 Progress", "0 / 0"),
            ("⚡ Speed", "0/s"),
            ("🔒 Status", "Scanning")
        ]
        
        for i, (label, value) in enumerate(stats):
            frame = tk.Frame(stats_frame, bg="#222222", relief="groove", bd=2)
            frame.grid(row=i//3, column=i%3, padx=10, pady=5, ipadx=20, sticky="nsew")
            
            tk.Label(
                frame,
                text=label,
                bg="#222222",
                fg="white",
                font=("Segoe UI", 10)
            ).pack()
            
            self.stats_labels[label] = tk.Label(
                frame,
                text=value,
                bg="#222222",
                fg="#00ff88",
                font=("Segoe UI", 14, "bold")
            )
            self.stats_labels[label].pack()
        
        # Results Frame
        results_frame = tk.Frame(self.frame, bg="#1a1a1a")
        results_frame.pack(pady=15, fill="both", expand=True, padx=50)
        
        # Results header with buttons
        header_frame = tk.Frame(results_frame, bg="#1a1a1a")
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame,
            text="📋 Scan Results",
            bg="#1a1a1a",
            fg="white",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")
        
        # Clear results button
        tk.Button(
            header_frame,
            text="🗑️ Clear",
            command=self.clear_results,
            bg="#333333",
            fg="white",
            font=("Segoe UI", 9),
            cursor="hand2"
        ).pack(side="right")
        
        # Text widget with scrollbar
        text_frame = tk.Frame(results_frame, bg="#1a1a1a")
        text_frame.pack(fill="both", expand=True, pady=5)
        
        self.result_text = tk.Text(
            text_frame,
            bg="#0d0d0d",
            fg="white",
            height=10,
            wrap="word",
            font=("Consolas", 9),
            relief="flat"
        )
        self.result_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=self.result_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Configure tags for different statuses
        self.result_text.tag_config("Infected", foreground="#ff4444")
        self.result_text.tag_config("Suspicious", foreground="#ff8800")
        self.result_text.tag_config("Potential Risk", foreground="#ffcc00")
        self.result_text.tag_config("Safe", foreground="#44ff44")
        self.result_text.tag_config("Error", foreground="#ff0000")
        
        # Control Buttons
        control_frame = tk.Frame(self.frame, bg="#1a1a1a")
        control_frame.pack(pady=10)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="🛑 Stop Scan",
            command=self.stop_scan,
            width=15,
            height=2,
            bg="#cc0000",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            state="disabled",
            cursor="hand2"
        )
        self.stop_btn.pack(side="left", padx=10)
        
        self.export_btn = tk.Button(
            control_frame,
            text="📊 Export Report",
            command=self.export_report,
            width=15,
            height=2,
            bg="#333333",
            fg="white",
            font=("Segoe UI", 11),
            cursor="hand2"
        )
        self.export_btn.pack(side="left", padx=10)
        
        self.quarantine_btn = tk.Button(
            control_frame,
            text="📁 Quarantine All",
            command=self.quarantine_all,
            width=15,
            height=2,
            bg="#cc6600",
            fg="white",
            font=("Segoe UI", 11),
            cursor="hand2"
        )
        self.quarantine_btn.pack(side="left", padx=10)
    
    def show_scan_report(self, stats, threats):
        """Display full scan report in new window"""
        report_window = tk.Toplevel(self.frame)
        report_window.title("📊 Scan Report")
        report_window.geometry("700x550")
        report_window.configure(bg="#1a1a1a")
        report_window.resizable(False, False)
        
        # Make window modal
        report_window.transient(self.frame.winfo_toplevel())
        report_window.grab_set()
        
        # Header
        header = tk.Frame(report_window, bg="#1a1a1a")
        header.pack(fill="x", pady=20)
        
        tk.Label(
            header,
            text="📊 SCAN REPORT",
            bg="#1a1a1a",
            fg="cyan",
            font=("Segoe UI", 24, "bold")
        ).pack()
        
        tk.Label(
            header,
            text=f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            bg="#1a1a1a",
            fg="gray",
            font=("Segoe UI", 11)
        ).pack()
        
        # Stats
        stats_frame = tk.Frame(report_window, bg="#1a1a1a")
        stats_frame.pack(pady=15)
        
        stats_items = [
            ("📁 Files Scanned", str(stats['scanned']), "#00aaff"),
            ("⚠️ Threats Found", str(len(threats)), "#ff8800"),
            ("⏱️ Time Taken", f"{stats['elapsed_time']:.2f}s", "#aa66ff"),
            ("📊 Status", "✅ Complete" if len(threats) == 0 else "⚠️ Threats Found", "#00ff88" if len(threats) == 0 else "#ff8800")
        ]
        
        for i, (label, value, color) in enumerate(stats_items):
            frame = tk.Frame(stats_frame, bg="#222222", relief="groove", bd=2)
            frame.grid(row=i//2, column=i%2, padx=15, pady=8, ipadx=30, ipady=5)
            
            tk.Label(
                frame,
                text=label,
                bg="#222222",
                fg="#888888",
                font=("Segoe UI", 11)
            ).pack()
            
            tk.Label(
                frame,
                text=value,
                bg="#222222",
                fg=color,
                font=("Segoe UI", 18, "bold")
            ).pack()
        
        # Threats list
        if threats:
            tk.Label(
                report_window,
                text="🚨 Detected Threats",
                bg="#1a1a1a",
                fg="#ff4444",
                font=("Segoe UI", 14, "bold")
            ).pack(anchor="w", padx=30, pady=10)
            
            threat_frame = tk.Frame(report_window, bg="#1a1a1a")
            threat_frame.pack(fill="both", expand=True, padx=30)
            
            # Create listbox with scrollbar
            list_frame = tk.Frame(threat_frame, bg="#1a1a1a")
            list_frame.pack(fill="both", expand=True)
            
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side="right", fill="y")
            
            threat_listbox = tk.Listbox(
                list_frame,
                bg="#0d0d0d",
                fg="white",
                font=("Consolas", 10),
                yscrollcommand=scrollbar.set,
                height=8
            )
            threat_listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=threat_listbox.yview)
            
            for threat in threats:
                threat_listbox.insert(
                    "end",
                    f"⚠️ {threat['file'].split('/')[-1].split('\\')[-1]} - {threat.get('threat_name', 'Unknown')}"
                )
        else:
            # Clean report
            clean_frame = tk.Frame(report_window, bg="#1a1a1a")
            clean_frame.pack(pady=30)
            
            tk.Label(
                clean_frame,
                text="✅ No threats detected!",
                bg="#1a1a1a",
                fg="#00ff88",
                font=("Segoe UI", 20, "bold")
            ).pack()
            
            tk.Label(
                clean_frame,
                text="Your system is clean and secure",
                bg="#1a1a1a",
                fg="gray",
                font=("Segoe UI", 12)
            ).pack()
        
        # Close button
        tk.Button(
            report_window,
            text="✅ Close Report",
            command=report_window.destroy,
            width=20,
            height=2,
            bg="#0066cc",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            cursor="hand2"
        ).pack(pady=20)
    
    def update_progress(self, result):
        """Update progress bar and status"""
        stats = self.scanner.get_stats()
        
        # Calculate speed
        current_time = datetime.now()
        time_diff = (current_time - self.last_time).total_seconds()
        files_diff = stats['scanned'] - self.last_count
        
        if time_diff > 0:
            speed = files_diff / time_diff if files_diff > 0 else 0
            self.stats_labels["⚡ Speed"].config(text=f"{speed:.1f}/s")
        
        self.last_count = stats['scanned']
        self.last_time = current_time
        
        # Update progress
        if stats['total'] > 0:
            progress_value = (stats['scanned'] / stats['total']) * 100
            self.progress['value'] = min(progress_value, 100)
        
        self.stats_labels["📁 Scanned"].config(text=str(stats['scanned']))
        self.stats_labels["⚠️ Threats"].config(text=str(len(self.scanner.threats_found)))
        self.stats_labels["📊 Progress"].config(text=f"{stats['scanned']} / {stats['total']}")
        
        if stats['elapsed_time'] > 0:
            minutes = int(stats['elapsed_time'] // 60)
            seconds = int(stats['elapsed_time'] % 60)
            self.stats_labels["⏱️ Time"].config(text=f"{minutes:02d}:{seconds:02d}")
        
        # Update status
        if stats['is_scanning']:
            self.stats_labels["🔒 Status"].config(text="🔄 Scanning")
        else:
            self.stats_labels["🔒 Status"].config(text="✅ Complete")
        
        # Show current file
        if stats['current_file']:
            filename = stats['current_file'].split('/')[-1].split('\\')[-1]
            self.file_label.config(text=f"📄 {filename[:50]}...")
        
        # Display result
        if result:
            status = result['status']
            status_emoji = "⚠️" if status in ['Infected', 'Suspicious'] else "✅"
            
            result_text = f"[{datetime.now().strftime('%H:%M:%S')}] {status_emoji} "
            result_text += f"{result['file'].split('/')[-1].split('\\')[-1][:40]} - {status}"
            
            if status in ['Infected', 'Suspicious']:
                result_text += f" 🚨 {result.get('threat_name', 'Unknown')}"
                if 'severity' in result:
                    result_text += f" [{result['severity']}]"
            
            self.result_text.insert("1.0", result_text + "\n")
            self.result_text.tag_add(status, "1.0", "end")
    
    def scan_thread_func(self, scan_func, *args):
        """Run scan in separate thread"""
        try:
            self.scanning = True
            self.stop_btn.config(state="normal")
            self.result_text.delete("1.0", "end")
            
            self.scanner.clear_threats()
            self.progress['value'] = 0
            self.stats_labels["⏱️ Time"].config(text="00:00")
            self.stats_labels["⚡ Speed"].config(text="0/s")
            self.last_count = 0
            self.last_time = datetime.now()
            
            self.status_label.config(text="🔍 Scanning...", fg="yellow")
            
            if args:
                scan_func(args[0], self.update_progress)
            else:
                scan_func(self.update_progress)
            
            if not self.scanner.scanning:
                self.status_label.config(text="✅ Scan Complete!", fg="lime")
                self.progress['value'] = 100
                
                stats = self.scanner.get_stats()
                threat_count = len(self.scanner.threats_found)
                
                # Show summary
                summary = f"\n{'='*60}\n"
                summary += f"📊 SCAN COMPLETE\n"
                summary += f"{'='*60}\n"
                summary += f"📁 Files Scanned: {stats['scanned']}\n"
                summary += f"⚠️ Threats Found: {threat_count}\n"
                summary += f"⏱️ Time Taken: {stats['elapsed_time']:.2f} seconds\n"
                summary += f"⚡ Avg Speed: {stats['scanned']/stats['elapsed_time']:.1f} files/sec\n"
                
                if threat_count > 0:
                    summary += f"\n🚨 THREATS DETECTED:\n"
                    summary += f"{'─'*60}\n"
                    for i, threat in enumerate(self.scanner.threats_found, 1):
                        summary += f"{i}. 📄 {threat['file'].split('/')[-1].split('\\')[-1]}\n"
                        summary += f"   🔴 Threat: {threat.get('threat_name', 'Unknown')}\n"
                        summary += f"   ⚠️ Severity: {threat.get('severity', 'Unknown')}\n"
                        summary += f"   📊 Score: {threat['score']}%\n"
                        summary += f"{'─'*60}\n"
                    summary += f"\n💡 Click 'Quarantine All' to secure your system."
                else:
                    summary += f"\n✅ No threats detected. System is clean!\n"
                
                summary += f"{'='*60}\n"
                self.result_text.insert("end", summary)
                
                self.stats_labels["📁 Scanned"].config(text=str(stats['scanned']))
                self.stats_labels["⚠️ Threats"].config(text=str(threat_count))
                self.stats_labels["🔒 Status"].config(text="✅ Complete")
                
                # Save to database
                if self.db:
                    try:
                        scan_id = self.db.insert_scan_history(
                            scan_type='manual',
                            files_scanned=stats['scanned'],
                            threats_found=threat_count,
                            scan_duration=stats['elapsed_time'],
                            status='completed'
                        )
                        
                        for threat in self.scanner.threats_found:
                            self.db.insert_threat(
                                file_path=threat['file'],
                                threat_name=threat.get('threat_name', 'Unknown'),
                                severity=threat.get('severity', 'Medium'),
                                threat_type=threat.get('threat_type', 'Unknown'),
                                scan_id=scan_id,
                                hash_value=threat.get('hash'),
                                file_size=os.path.getsize(threat['file']) if os.path.exists(threat['file']) else None
                            )
                        
                        self.db.insert_activity('scan_completed', f'{stats["scanned"]} files, {threat_count} threats')
                    except Exception as e:
                        print(f"Failed to save scan to database: {e}")
                
                # Show scan report window
                self.frame.after(500, lambda: self.show_scan_report(stats, self.scanner.threats_found))
            
        except Exception as e:
            self.status_label.config(text=f"❌ Error: {str(e)}", fg="red")
            self.result_text.insert("end", f"\n❌ ERROR: {str(e)}\n")
        finally:
            self.scanning = False
            self.stop_btn.config(state="disabled")
    
    def quick_scan(self):
        if self.scanning:
            return
        self.scan_thread = threading.Thread(
            target=self.scan_thread_func,
            args=(self.scanner.scan_system_fast,)
        )
        self.scan_thread.start()
    
    def full_scan(self):
        if self.scanning:
            return
        self.scan_thread = threading.Thread(
            target=self.scan_thread_func,
            args=(self.scanner.scan_full_system_fast,)
        )
        self.scan_thread.start()
    
    def custom_scan(self):
        if self.scanning:
            return
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if folder:
            self.scan_thread = threading.Thread(
                target=self.scan_thread_func,
                args=(self.scanner.scan_folder_fast, folder)
            )
            self.scan_thread.start()
    
    def memory_scan(self):
        if self.scanning:
            return
        self.scan_thread = threading.Thread(
            target=self.scan_thread_func,
            args=(self.scanner.scan_memory,)
        )
        self.scan_thread.start()
    
    def stop_scan(self):
        if self.scanning:
            self.scanner.stop_scan()
            self.status_label.config(text="⏹️ Scan Stopped", fg="orange")
            self.stop_btn.config(state="disabled")
            self.stats_labels["🔒 Status"].config(text="⏹️ Stopped")
    
    def clear_results(self):
        self.result_text.delete("1.0", "end")
    
    def export_report(self):
        if not self.scanner.threats_found and self.scanner.scanned_count == 0:
            messagebox.showinfo("No Data", "No scan results to export.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write("="*70 + "\n")
                    f.write("          NEXUS ANTIVIRUS - SCAN REPORT\n")
                    f.write("="*70 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Files Scanned: {self.scanner.scanned_count}\n")
                    f.write(f"Threats Found: {len(self.scanner.threats_found)}\n")
                    f.write(f"Scan Duration: {self.scanner.elapsed_time:.2f} seconds\n")
                    f.write("="*70 + "\n\n")
                    
                    if self.scanner.threats_found:
                        f.write("🚨 THREATS DETECTED:\n")
                        f.write("─"*70 + "\n")
                        for i, threat in enumerate(self.scanner.threats_found, 1):
                            f.write(f"\n{i}. FILE: {threat['file']}\n")
                            f.write(f"   Threat: {threat.get('threat_name', 'Unknown')}\n")
                            f.write(f"   Severity: {threat.get('severity', 'Unknown')}\n")
                            f.write(f"   Score: {threat['score']}%\n")
                            f.write(f"   Type: {threat.get('threat_type', 'Unknown')}\n")
                            f.write(f"   Hash: {threat.get('hash', 'N/A')}\n")
                            f.write("   " + "─"*66 + "\n")
                    else:
                        f.write("✅ No threats detected. System is clean!\n")
                    
                    f.write("\n" + "="*70 + "\n")
                    f.write("Report generated by Nexus Antivirus\n")
                    f.write("="*70 + "\n")
                
                self.status_label.config(text="📊 Report exported!", fg="green")
                messagebox.showinfo("Success", f"Report saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def quarantine_all(self):
        """Quarantine all detected threats with feedback"""
        threats = self.scanner.get_threats()
        if not threats:
            messagebox.showinfo("No Threats", "No threats to quarantine.")
            return
        
        if not messagebox.askyesno(
            "Confirm Quarantine",
            f"Move {len(threats)} detected threats to quarantine?"
        ):
            return
        
        success_count = 0
        failed_list = []
        for threat in threats:
            success, msg = self.scanner.quarantine_file(
                threat['file'],
                threat.get('threat_name', 'Unknown')
            )
            if success:
                success_count += 1
            else:
                failed_list.append(f"{threat['file']} - {msg}")
        
        if failed_list:
            messagebox.showwarning(
                "Partial Quarantine",
                f"Successfully quarantined {success_count} of {len(threats)} threats.\n\n"
                f"Failed items:\n" + "\n".join(failed_list[:5]) + 
                ("\n..." if len(failed_list) > 5 else "")
            )
        else:
            messagebox.showinfo(
                "Quarantine Complete",
                f"Successfully quarantined all {success_count} threats!"
            )
        
        # Clear threats after quarantine
        self.scanner.clear_threats()
        self.stats_labels["⚠️ Threats"].config(text="0")
        self.status_label.config(text="✅ Threats processed", fg="green")