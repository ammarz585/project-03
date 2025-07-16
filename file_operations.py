# file_operations.py
import os
import shutil
import tkinter as tk  # ✅ Needed for Label, Entry
from tkinter import simpledialog, messagebox
from gui_helpers import open_file_externally

class FileOperationsMixin:
    def add_folder(self):
        name = simpledialog.askstring("New Folder", "Enter folder name:")
        if not name:
            return
        path = os.path.join(self.current_path, name)
        try:
            os.mkdir(path)
            self.load_folder(self.current_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder:\n{e}")

    def add_file(self):
        name = simpledialog.askstring("New File", "Enter file name:")
        if not name:
            return
        path = os.path.join(self.current_path, name)
        try:
            with open(path, 'w'):
                pass
            self.load_folder(self.current_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create file:\n{e}")

    def rename_path(self, path):
        for widget in self.inner_frame.winfo_children():
            labels = [w for w in widget.winfo_children() if isinstance(w, tk.Label)]
            if labels and os.path.join(self.current_path, labels[-1].cget("text")) == path:
                name_label = labels[-1]

                name_label.pack_forget()
                entry = tk.Entry(widget, font=("Segoe UI", 9))
                entry.insert(0, name_label.cget("text"))
                entry.pack()
                entry.focus_set()

                def apply_rename(event=None):
                    new_name = entry.get().strip()
                    if not new_name or new_name == name_label.cget("text"):
                        entry.destroy()
                        name_label.pack()
                        return

                    new_path = os.path.join(os.path.dirname(path), new_name)
                    try:
                        os.rename(path, new_path)
                        self.load_folder(self.current_path)
                    except Exception as e:
                        messagebox.showerror("Rename Error", str(e))
                    finally:
                        entry.destroy()

                entry.bind("<Return>", apply_rename)
                entry.bind("<FocusOut>", apply_rename)
                break

    def delete_path(self, path):
        confirm = messagebox.askyesno("Delete", f"Delete:\n{path}?")
        if not confirm:
            return
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.load_folder(self.current_path)
        except Exception as e:
            messagebox.showerror("Delete Error", str(e))

    def open_selected_path(self, path):
        if os.path.isdir(path):
            self.load_folder(path)
            self.push_history(path)
        elif os.path.isfile(path):
            open_file_externally(path)
