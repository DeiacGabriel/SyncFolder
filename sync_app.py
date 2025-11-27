import os
import time
import shutil
import threading
import customtkinter as ctk
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ctk.set_appearance_mode("Dark")  # Modus: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class BiDirSyncHandler(FileSystemEventHandler):
    """
    Dieser Handler reagiert auf Dateiänderungen.
    Er verhindert Endlosschleifen, indem er prüft, ob die Zieldatei
    bereits identisch ist (Größe & Zeitstempel).
    """
    def __init__(self, source_folder, target_folder, logger_func):
        self.source_folder = source_folder
        self.target_folder = target_folder
        self.log = logger_func

    def _is_identical(self, src_path, dest_path):
        """Prüft, ob Datei existiert und identisch ist, um Loops zu vermeiden."""
        if not os.path.exists(dest_path):
            return False
        s_stat = os.stat(src_path)
        d_stat = os.stat(dest_path)
        return (s_stat.st_size == d_stat.st_size and 
                abs(s_stat.st_mtime - d_stat.st_mtime) < 1.0)

    def on_created(self, event):
        self._process_event(event)

    def on_modified(self, event):
        self._process_event(event)

    def _process_event(self, event):
        if event.is_directory:
            return

        relative_path = os.path.relpath(event.src_path, self.source_folder)
        dest_path = os.path.join(self.target_folder, relative_path)

        try:
            if self._is_identical(event.src_path, dest_path):
                return

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            time.sleep(0.1) 
            
            shutil.copy2(event.src_path, dest_path)
            self.log(f"AUTO-SYNC: {relative_path} -> gespiegelt.")
            
        except Exception as e:
            self.log(f"FEHLER bei {relative_path}: {e}")

class SyncPair:
    """Verwaltet ein Paar von Ordnern (A <-> B)"""
    def __init__(self, folder_a, folder_b, logger_func):
        self.folder_a = folder_a
        self.folder_b = folder_b
        self.logger = logger_func
        self.observer_a = Observer()
        self.observer_b = Observer()
        self.is_running = False

    def start(self):
        if self.is_running: return
        
        handler_a = BiDirSyncHandler(self.folder_a, self.folder_b, self.logger)
        self.observer_a.schedule(handler_a, self.folder_a, recursive=True)
        
        handler_b = BiDirSyncHandler(self.folder_b, self.folder_a, self.logger)
        self.observer_b.schedule(handler_b, self.folder_b, recursive=True)

        self.observer_a.start()
        self.observer_b.start()
        self.is_running = True
        self.logger(f"Start: Überwachung zwischen '{os.path.basename(self.folder_a)}' und '{os.path.basename(self.folder_b)}'")

    def stop(self):
        if not self.is_running: return
        self.observer_a.stop()
        self.observer_b.stop()
        self.observer_a.join()
        self.observer_b.join()
        self.is_running = False
        self.logger("Stop: Überwachung beendet.")

    def manual_sync(self):
        """Führt einen manuellen Abgleich beider Richtungen durch"""
        self.logger("Manueller Sync gestartet...")
        self._sync_tree(self.folder_a, self.folder_b)
        self._sync_tree(self.folder_b, self.folder_a)
        self.logger("Manueller Sync abgeschlossen.")

    def _sync_tree(self, src_root, dest_root):
        for root, dirs, files in os.walk(src_root):
            rel_path = os.path.relpath(root, src_root)
            dest_dir = os.path.join(dest_root, rel_path)

            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                
                if not os.path.exists(dest_file) or \
                   os.stat(src_file).st_mtime - os.stat(dest_file).st_mtime > 1.0:
                    try:
                        shutil.copy2(src_file, dest_file)
                        self.logger(f"MANUAL: {file} kopiert.")
                    except Exception as e:
                        self.logger(f"Fehler: {e}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Python Folder Mirror")
        self.geometry("700x500")
        
        self.sync_pairs = []

        self.create_widgets()

    def create_widgets(self):
        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.pack(pady=10, padx=10, fill="x")

        self.btn_folder1 = ctk.CTkButton(self.frame_inputs, text="Wähle Ordner 1", command=lambda: self.select_folder(1))
        self.btn_folder1.grid(row=0, column=0, padx=5, pady=5)
        
        self.lbl_folder1 = ctk.CTkLabel(self.frame_inputs, text="Kein Ordner gewählt", text_color="gray")
        self.lbl_folder1.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.btn_folder2 = ctk.CTkButton(self.frame_inputs, text="Wähle Ordner 2", command=lambda: self.select_folder(2))
        self.btn_folder2.grid(row=1, column=0, padx=5, pady=5)

        self.lbl_folder2 = ctk.CTkLabel(self.frame_inputs, text="Kein Ordner gewählt", text_color="gray")
        self.lbl_folder2.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.btn_add = ctk.CTkButton(self.frame_inputs, text="Spiegelung hinzufügen", fg_color="green", command=self.add_sync_pair)
        self.btn_add.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        self.lbl_list = ctk.CTkLabel(self, text="Aktive Spiegelungen:", font=("Arial", 14, "bold"))
        self.lbl_list.pack(pady=(10, 0))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=100)
        self.scroll_frame.pack(pady=5, padx=10, fill="x")

        self.btn_manual = ctk.CTkButton(self, text="Alles jetzt manuell syncen", command=self.trigger_manual_sync)
        self.btn_manual.pack(pady=5)

        self.textbox_log = ctk.CTkTextbox(self, height=150)
        self.textbox_log.pack(pady=10, padx=10, fill="both", expand=True)
        self.textbox_log.insert("0.0", "Bereit. Bitte Ordner auswählen...\n")

        self.path1_cache = ""
        self.path2_cache = ""

    def log_message(self, message):
        """Schreibt in das Textfeld (Thread-sicher)"""
        def _write():
            self.textbox_log.insert("end", message + "\n")
            self.textbox_log.see("end")
        self.after(0, _write)

    def select_folder(self, num):
        path = filedialog.askdirectory()
        if path:
            if num == 1:
                self.path1_cache = path
                self.lbl_folder1.configure(text=path, text_color="white")
            else:
                self.path2_cache = path
                self.lbl_folder2.configure(text=path, text_color="white")

    def add_sync_pair(self):
        """Fügt ein neues Spiegelungspaar hinzu"""
        if not self.path1_cache or not self.path2_cache:
            self.log_message("Fehler: Beide Ordner müssen ausgewählt sein.")
            return
        
        pair = SyncPair(self.path1_cache, self.path2_cache, self.log_message)
        pair.start()
        self.sync_pairs.append(pair)
        
        label = ctk.CTkLabel(self.scroll_frame, 
                           text=f"{os.path.basename(self.path1_cache)} <-> {os.path.basename(self.path2_cache)}")
        label.pack(pady=2)
        
        self.log_message(f"Spiegelung hinzugefügt: {self.path1_cache} <-> {self.path2_cache}")
        
        self.path1_cache = ""
        self.path2_cache = ""
        self.lbl_folder1.configure(text="Kein Ordner gewählt", text_color="gray")
        self.lbl_folder2.configure(text="Kein Ordner gewählt", text_color="gray")

    def trigger_manual_sync(self):
        """Führt manuellen Sync für alle Paare aus"""
        if not self.sync_pairs:
            self.log_message("Keine aktiven Spiegelungen vorhanden.")
            return
        
        def _sync():
            for pair in self.sync_pairs:
                pair.manual_sync()
        
        threading.Thread(target=_sync, daemon=True).start()

    def on_closing(self):
        """Stoppt alle Observer vor dem Schließen"""
        self.log_message("Beende alle Überwachungen...")
        for pair in self.sync_pairs:
            pair.stop()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()