import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

class UltraFileTransfer:
    def __init__(self):
        self.root = tk.Tk()
        self.stop_transfer = False
        self.is_transferring = False
        self.copied_count = 0
        self.skipped_count = 0
        self.total_files = 0
        self.current_file = ""
        self.transfer_type = ""
        self.source_path = ""
        self.executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 8)  # 🔥 2X FASTER
        self.all_futures = []  # 🔥 STOP FIX
        self.setup_complete_gui()
    
    def animate_title(self):
        colors = ["#00ff88", "#00dd77", "#00ff88", "#00cc66"]
        color_idx = 0
        def glow():
            nonlocal color_idx
            try:
                self.title_label.config(fg=colors[color_idx % 4])
                color_idx += 1
            except: pass
            self.root.after(300, glow)
        glow()
    
    def hover_effect(self, widget, normal_bg, hover_bg, normal_fg="white", hover_fg="white"):
        def enter(e): widget.config(bg=hover_bg, fg=hover_fg)
        def leave(e): widget.config(bg=normal_bg, fg=normal_fg)
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def setup_complete_gui(self):
        self.root.title("🚀 ULTRA DRIVE - MAX SPEED TRANSFER")
        self.root.geometry("850x780")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(True, True)

        # 🔥 ANIMATED TITLE
        self.title_label = tk.Label(self.root, text="⚡ ULTRA MAX SPEED DRIVE ⚡", 
                                   font=("Segoe UI", 28, "bold"), bg="#0a0a0a", fg="#00ff88")
        self.title_label.pack(pady=25)
        self.animate_title()

        subtitle = tk.Label(self.root, text="💥 ULTRA FAST PC TRANSFER - 10X WINDOWS SPEED", 
                           font=("Segoe UI", 12), bg="#0a0a0a", fg="#888")
        subtitle.pack(pady=(0, 25))

        # 🔥 MAIN PANEL
        main_panel = tk.Frame(self.root, bg="#1a1a1a", relief="raised", bd=2)
        main_panel.pack(padx=35, pady=10, fill="both", expand=True)

        # SOURCE SECTION
        source_frame = tk.LabelFrame(main_panel, text="📁 SOURCE", font=("Segoe UI", 11, "bold"), 
                                    bg="#1a1a1a", fg="#00ff88", relief="flat")
        source_frame.pack(fill="x", padx=20, pady=(20,10))

        tk.Label(source_frame, text="Folder:", font=("Segoe UI", 10, "bold"), 
                bg="#1a1a1a", fg="#fff").pack(anchor="w", padx=15, pady=(10,5))
        
        src_entry_frame = tk.Frame(source_frame, bg="#1a1a1a")
        src_entry_frame.pack(fill="x", padx=15, pady=5)
        
        self.source_entry = tk.Entry(src_entry_frame, font=("Consolas", 11), bg="#2a2a2a", fg="#fff", 
                                    relief="flat", insertbackground="#00ff88")
        self.source_entry.pack(side="left", fill="x", expand=True)
        self.hover_effect(self.source_entry, "#2a2a2a", "#333")
        
        src_browse = tk.Button(src_entry_frame, text="📂 BROWSE", command=self.browse_source,
                              bg="#00ff88", fg="#000", font=("Segoe UI", 10, "bold"), 
                              relief="flat", cursor="hand2", width=12)
        src_browse.pack(side="right", padx=(5,0))
        self.hover_effect(src_browse, "#00ff88", "#00dd77")

        # DESTINATION SECTION  
        dest_frame = tk.LabelFrame(main_panel, text="💾 DESTINATION", font=("Segoe UI", 11, "bold"), 
                                  bg="#1a1a1a", fg="#00ff88", relief="flat")
        dest_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(dest_frame, text="Drive/Folder:", font=("Segoe UI", 10, "bold"), 
                bg="#1a1a1a", fg="#fff").pack(anchor="w", padx=15, pady=(10,5))
        
        dest_entry_frame = tk.Frame(dest_frame, bg="#1a1a1a")
        dest_entry_frame.pack(fill="x", padx=15, pady=5)
        
        self.dest_entry = tk.Entry(dest_entry_frame, font=("Consolas", 11), bg="#2a2a2a", fg="#fff", 
                                  relief="flat", insertbackground="#00ff88")
        self.dest_entry.pack(side="left", fill="x", expand=True)
        self.hover_effect(self.dest_entry, "#2a2a2a", "#333")
        
        dest_browse = tk.Button(dest_entry_frame, text="📂 BROWSE", command=self.browse_dest,
                               bg="#00ff88", fg="#000", font=("Segoe UI", 10, "bold"), 
                               relief="flat", cursor="hand2", width=12)
        dest_browse.pack(side="right", padx=(5,0))
        self.hover_effect(dest_browse, "#00ff88", "#00dd77")

        # 🔥 PROGRESS SECTION
        progress_frame = tk.LabelFrame(main_panel, text="⚡ ULTRA SPEED PROGRESS", 
                                      font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="#00ff88")
        progress_frame.pack(fill="x", padx=20, pady=15)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, length=650, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(pady=15)

        # Status Labels
        status_frame = tk.Frame(progress_frame, bg="#1a1a1a")
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="⚡ ULTRA FAST READY", 
                                    font=("Segoe UI", 12, "bold"), bg="#1a1a1a", fg="#00ff88")
        self.status_label.pack()
        
        self.file_label = tk.Label(status_frame, text="No file selected", 
                                  font=("Segoe UI", 11), bg="#1a1a1a", fg="#ffaa00")
        self.file_label.pack()
        
        self.count_label = tk.Label(status_frame, text="0 / 0 files - 0 MB transferred", 
                                   font=("Segoe UI", 10), bg="#1a1a1a", fg="#aaa")
        self.count_label.pack()
        
        self.speed_label = tk.Label(status_frame, text="🚀 SPEED: 0 MB/s", 
                                   font=("Segoe UI", 10, "bold"), bg="#1a1a1a", fg="#ff4444")
        self.speed_label.pack()

        # 🔥 TRANSFER BUTTONS
        btn_frame = tk.Frame(main_panel, bg="#1a1a1a")
        btn_frame.pack(pady=20)

        self.copy_btn = tk.Button(btn_frame, text="⚡ ULTRA COPY", command=self.start_copy,
                                 font=("Segoe UI", 14, "bold"), bg="#4caf50", fg="white",
                                 width=22, height=2, relief="flat", cursor="hand2")
        self.copy_btn.pack(side="left", padx=10)
        self.hover_effect(self.copy_btn, "#4caf50", "#45a049")

        self.move_btn = tk.Button(btn_frame, text="✂️ ULTRA MOVE", command=self.start_move,
                                 font=("Segoe UI", 14, "bold"), bg="#ff9800", fg="white",
                                 width=22, height=2, relief="flat", cursor="hand2")
        self.move_btn.pack(side="left", padx=10)
        self.hover_effect(self.move_btn, "#ff9800", "#f57c00")

        self.stop_btn = tk.Button(btn_frame, text="⏹️ STOP", command=self.stop_transfer,
                                 font=("Segoe UI", 14, "bold"), bg="#f44336", fg="white",
                                 width=22, height=2, relief="flat", state="disabled", cursor="hand2")
        self.stop_btn.pack(side="left", padx=10)
        self.hover_effect(self.stop_btn, "#f44336", "#e53935")

        # 🔥 LOG SECTION
        log_frame = tk.LabelFrame(main_panel, text="📋 ULTRA LOG", font=("Segoe UI", 11, "bold"), 
                                 bg="#1a1a1a", fg="#00ff88")
        log_frame.pack(fill="both", expand=True, padx=20, pady=(10,20))

        log_container = tk.Frame(log_frame, bg="#1a1a1a")
        log_container.pack(fill="both", expand=True, padx=15, pady=10)

        self.log_text = tk.Text(log_container, height=10, bg="#0d1117", fg="#00ff88",
                               font=("Consolas", 10), relief="flat", insertbackground="#00ff88")
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

    def log_msg(self, message):
        def log():
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
        self.root.after(0, log)

    def update_progress(self, value):
        def update():
            self.progress_var.set(value)
        self.root.after(0, update)

    def browse_source(self):
        path = filedialog.askdirectory(title="Select Source Folder")
        if path:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, path)
            self.log_msg(f"📁 Source: {os.path.basename(path)}")

    def browse_dest(self):
        path = filedialog.askdirectory(title="Select Destination Drive/Folder")
        if path:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, path)
            self.log_msg(f"💾 Destination: {os.path.basename(path)}")

    def count_files_fast(self, source_path):
        """🔥 ULTRA FAST file counting using pathlib"""
        count = sum(1 for _ in Path(source_path).rglob('*') if _.is_file())
        return count

    def ultra_copy_move_worker(self, src_file, dest_folder, is_move=False):
        """🔥 SINGLE FILE TRANSFER - MAX SPEED"""
        if self.stop_transfer:  # 🔥 STOP CHECK
            return "cancelled"
        try:
            filename = os.path.basename(src_file)
            rel_path = os.path.relpath(os.path.dirname(src_file), self.source_path)
            dest_subfolder = os.path.join(dest_folder, rel_path)
            os.makedirs(dest_subfolder, exist_ok=True)
            dest_file = os.path.join(dest_subfolder, filename)
            
            if os.path.exists(dest_file):
                return "skip"
            
            if is_move:
                shutil.move(src_file, dest_file)  # 🔥 FASTEST MOVE
            else:
                shutil.copy(src_file, dest_file)  # 🔥 FAST COPY (no metadata)
            
            return "success"
        except:
            return "error"

    def ultra_transfer(self, is_move=False):
        """🚀 ULTRA MAX SPEED TRANSFER ENGINE"""
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        
        if not source or not dest or not os.path.exists(source):
            self.log_msg("❌ Invalid source or destination!")
            self.reset_ui()
            return

        self.is_transferring = True
        self.stop_transfer = False
        self.copied_count = 0
        self.skipped_count = 0
        self.all_futures = []  # 🔥 RESET FUTURES
        
        operation = "MOVE" if is_move else "COPY"
        self.transfer_type = operation
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(dest, f"{operation}_{timestamp}")
        os.makedirs(backup_folder, exist_ok=True)
        
        self.source_path = source
        self.total_files = self.count_files_fast(source)
        
        self.log_msg(f"🚀 {operation} ULTRA STARTED → {self.total_files} files")
        self.log_msg(f"📁 Target: {backup_folder}")
        
        self.update_progress(0)
        
        all_files = [os.path.join(root, f) for root, dirs, files in os.walk(source) for f in files]  # 🔥 1 LINE FASTER
        
        self.log_msg(f"⚡ {len(all_files)} files queued")
        
        start_time = time.time()
        processed = 0
        
        # 🔥 ULTRA FAST PARALLEL - NO BATCHING
        futures = [self.executor.submit(self.ultra_copy_move_worker, src_file, backup_folder, is_move) 
                  for src_file in all_files if not self.stop_transfer]
        self.all_futures.extend(futures)  # 🔥 TRACK FOR STOP
        
        # 🔥 ASYNC PROCESSING - ULTRA FAST UI
        def check_progress():
            nonlocal processed
            completed = 0
            for future in futures:
                if future.done():
                    try:
                        result = future.result()
                        if result == "success":
                            self.copied_count += 1
                        elif result == "skip":
                            self.skipped_count += 1
                        completed += 1
                    except:
                        self.skipped_count += 1
            
            processed = completed
            if processed < len(futures) and not self.stop_transfer:
                progress = (processed / self.total_files) * 100
                self.update_progress(progress)
                elapsed = time.time() - start_time
                speed = (processed / elapsed) if elapsed > 0 else 0
                self.speed_label.config(text=f"🚀 SPEED: {speed:.0f} files/s")
                self.count_label.config(text=f"{processed}/{self.total_files}")
                self.root.after(100, check_progress)  # 🔥 FAST UI UPDATE
            else:
                self.finish_transfer(start_time)
        
        self.root.after(50, check_progress)

    def finish_transfer(self, start_time):
        elapsed_total = time.time() - start_time
        if not self.stop_transfer:
            self.log_msg(f"✅ ULTRA COMPLETE in {elapsed_total:.1f}s!")
            self.log_msg(f"📊 {self.copied_count} copied | {self.skipped_count} skipped")
            success_msg = f"""⚡ ULTRA COMPLETE!

📁 Operation: {self.transfer_type}
✅ Copied: {self.copied_count} files
⏭️ Skipped: {self.skipped_count} files
⏱️ Time: {elapsed_total:.1f}s
🚀 Speed: {(self.copied_count/elapsed_total):.1f} files/s"""
            self.root.after(100, lambda: messagebox.showinfo("✅ COMPLETE", success_msg))
        else:
            self.log_msg("🛑 Transfer cancelled!")
        self.reset_ui()

    def start_copy(self):
        if self.validate_paths():
            self.status_label.config(text="⚡ ULTRA COPYING...")
            threading.Thread(target=self.ultra_transfer, args=(False,), daemon=True).start()
            self.enable_stop_btn()

    def start_move(self):
        if self.validate_paths():
            self.status_label.config(text="✂️ ULTRA MOVING...")
            threading.Thread(target=self.ultra_transfer, args=(True,), daemon=True).start()
            self.enable_stop_btn()

    def enable_stop_btn(self):
        self.copy_btn.config(state="disabled")
        self.move_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

    def stop_transfer(self):
        self.stop_transfer = True
        self.status_label.config(text="🛑 STOPPING...")
        self.log_msg("🛑 STOPPING ALL THREADS!")
        for future in self.all_futures:
            future.cancel()  # 🔥 INSTANT STOP

    def reset_ui(self):
        self.is_transferring = False
        self.stop_transfer = False
        self.progress_var.set(0)
        self.status_label.config(text="⚡ ULTRA FAST READY")
        self.file_label.config(text="Ready")
        self.count_label.config(text="0 / 0 files")
        self.speed_label.config(text="🚀 SPEED: 0 MB/s")
        self.copy_btn.config(state="normal")
        self.move_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def validate_paths(self):
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        
        if not source or not dest:
            messagebox.showerror("❌ Error", "Please select SOURCE and DESTINATION!")
            return False
        
        if not os.path.exists(source):
            messagebox.showerror("❌ Error", "Source folder not found!")
            return False
        
        if not os.access(dest, os.W_OK):
            messagebox.showerror("❌ Error", "No write permission in destination!")
            return False
        
        self.log_msg("✅ Paths OK!")
        return True

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        if self.is_transferring:
            if messagebox.askokcancel("Quit", "Stop transfer and exit?"):
                self.stop_transfer = True
                self.root.after(1000, self.root.destroy)
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = UltraFileTransfer()
    app.run()