# search_operations.py
import os
import tkinter as tk
from tkinter import messagebox
from gui_helpers import open_file_externally

class SearchOperationsMixin:
    def search_items(self):
        term = self.search_var.get().strip()
        if not term or term == self.search_placeholder:
            messagebox.showinfo("Search", "Enter valid search term.")
            return

        results = []

        def recursive_search(path):
            try:
                for item in os.listdir(path):
                    full = os.path.join(path, item)
                    if term.lower() in item.lower():
                        results.append((item, full))
                    if os.path.isdir(full):
                        recursive_search(full)
            except PermissionError:
                pass

        if self.current_path:
            recursive_search(self.current_path)

        if not results:
            messagebox.showinfo("Search", f"No items found for '{term}'")
        else:
            self.show_search_results(results)

    def show_search_results(self, results):
        # ✅ Close existing search popup if it's open
        if hasattr(self, "search_popup") and self.search_popup and self.search_popup.winfo_exists():
            self.search_popup.destroy()

        self.search_popup = tk.Toplevel(self.root)
        self.search_popup.title(f"Search Results ({len(results)})")
        self.search_popup.geometry("500x300")

        scrollbar = tk.Scrollbar(self.search_popup)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(self.search_popup, yscrollcommand=scrollbar.set, font=("Segoe UI", 10))
        for text, path in results:
            listbox.insert(tk.END, f"{text} — {path}")
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        def open_selected(event=None):
            sel = listbox.curselection()
            if not sel:
                return
            _, path = results[sel[0]]
            try:
                open_file_externally(path)
            except Exception as e:
                messagebox.showerror("Open Error", str(e))

        open_btn = tk.Button(self.search_popup, text="Open Selected", command=open_selected)
        open_btn.pack(pady=10)
