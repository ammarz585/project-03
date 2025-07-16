# file_explorer_core.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from gui_helpers import get_icon_for_file, open_file_externally
from file_operations import FileOperationsMixin
from search_operations import SearchOperationsMixin

class FileExplorerApp(tk.Frame, FileOperationsMixin, SearchOperationsMixin):
    def __init__(self, root, folder_icon, search_icon):
        super().__init__(root)
        self.root = root
        self.folder_icon = folder_icon
        self.search_icon = search_icon

        self.history = []
        self.history_index = -1
        self.current_path = None
        self.selected_item = None
        self.icon_refs = {}

        self.root.title("📁 Recursive File Explorer")
        self.root.geometry("700x600")

        # === Top Frame ===
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, pady=5)

        title_label = tk.Label(top_frame, text="📁 Recursive File Explorer", font=("Segoe UI", 20, "bold"))
        title_label.pack(side=tk.LEFT, padx=10)

        right_btn_frame = tk.Frame(top_frame)
        right_btn_frame.pack(side=tk.RIGHT, padx=10)

        self.btn_back = tk.Button(right_btn_frame, text="←", width=3, command=self.go_back, state=tk.DISABLED)
        self.btn_back.pack(side=tk.LEFT, padx=2)

        self.btn_forward = tk.Button(right_btn_frame, text="→", width=3, command=self.go_forward, state=tk.DISABLED)
        self.btn_forward.pack(side=tk.LEFT, padx=2)

        self.btn_add_folder = tk.Button(right_btn_frame, text="➕ Folder", command=self.add_folder, state=tk.DISABLED)
        self.btn_add_folder.pack(side=tk.LEFT, padx=5)

        self.btn_add_file = tk.Button(right_btn_frame, text="➕ File", command=self.add_file, state=tk.DISABLED)
        self.btn_add_file.pack(side=tk.LEFT, padx=5)

        # === Search ===
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, pady=5)

        self.search_var = tk.StringVar()
        self.search_placeholder = "🔍 Search files or folders..."

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 12),
            width=40,
            relief=tk.RIDGE,
            bd=2
        )
        self.search_entry.insert(0, self.search_placeholder)
        self.search_entry.bind("<FocusIn>", self.clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_search_placeholder)
        self.search_entry.bind("<Return>", self.on_search_enter)
        self.search_entry.config(state=tk.DISABLED)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        search_button = tk.Button(
            search_frame,
            image=self.search_icon,
            command=self.handle_search_click,
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        search_button.pack(side=tk.LEFT, padx=5)
        self.search_button = search_button

        # === Folder Selector Frame ===
        folder_selector_frame = tk.Frame(self.root)
        folder_selector_frame.pack(fill=tk.X, pady=5)

        self.folder_paths = []
        self.folder_buttons_frame = tk.Frame(folder_selector_frame)
        self.folder_buttons_frame.pack(fill=tk.X)

        self.add_multi_btn = tk.Button(folder_selector_frame, text="📂 Add More Folders", command=self.add_multiple_folders)
        self.add_multi_btn.pack(pady=5)

        # === Canvas Explorer ===
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)

        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", self.on_frame_configure)

        self.root.bind_all("<Control-Left>", lambda e: self.go_back())
        self.root.bind_all("<Control-Right>", lambda e: self.go_forward())
        self.inner_frame.bind("<Button-3>", self.show_context_menu_canvas)

        self.try_initial_folder()

    def try_initial_folder(self):
        folder = filedialog.askdirectory(title="Select Root Folder")
        if folder:
            self.folder_paths.append(folder)
            self.create_folder_button(folder)
            self.open_folder_path(folder)

    def add_multiple_folders(self):
        folder = filedialog.askdirectory(title="Select Folder to Add")
        if folder and folder not in self.folder_paths:
            self.folder_paths.append(folder)
            self.create_folder_button(folder)

    def create_folder_button(self, folder):
        frame = tk.Frame(self.folder_buttons_frame, bg="white")
        frame.pack(side=tk.LEFT, padx=5)

        icon_label = tk.Label(frame, image=self.folder_icon, bg="white", cursor="hand2")
        icon_label.pack()
    # Bind click on icon label to open folder
        icon_label.bind("<Button-1>", lambda e, f=folder: self.open_folder_path(f))

        text_btn = tk.Button(frame, text=os.path.basename(folder), command=lambda f=folder: self.open_folder_path(f), relief=tk.GROOVE)
        text_btn.pack()

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def clear_search_placeholder(self, event):
        if self.search_var.get() == self.search_placeholder:
            self.search_entry.delete(0, tk.END)

    def add_search_placeholder(self, event):
        if not self.search_var.get():
            self.search_entry.insert(0, self.search_placeholder)

    def open_folder_path(self, folder):
        self.btn_add_folder.config(state=tk.NORMAL)
        self.btn_add_file.config(state=tk.NORMAL)
        self.search_entry.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL)
        self.load_folder(folder)
        self.push_history(folder)

    def clear_explorer_view(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.icon_refs.clear()
        self.selected_item = None

    def load_folder(self, folder_path):
        self.current_path = folder_path
        self.clear_explorer_view()

        try:
            items = sorted(os.listdir(folder_path), key=str.lower)
        except PermissionError:
            messagebox.showerror("Permission Denied", f"Cannot access: {folder_path}")
            return

        icon_size = 64
        padding_x = 30
        padding_y = 60
        columns = max(1, self.canvas.winfo_width() // (icon_size + padding_x))
        if columns == 0:
            columns = 10

        row, col = 0, 0
        for item in items:
            full_path = os.path.join(folder_path, item)
            icon_img = self.folder_icon if os.path.isdir(full_path) else get_icon_for_file(full_path)
            self.icon_refs[item] = icon_img

            item_frame = tk.Frame(self.inner_frame, width=icon_size+10, height=padding_y, bg="white")
            item_frame.grid(row=row, column=col, padx=10, pady=10)
            item_frame.grid_propagate(False)

            icon_label = tk.Label(item_frame, image=icon_img, bg="white")
            icon_label.pack()

            text_label = tk.Label(item_frame, text=item, bg="white", wraplength=icon_size+20)
            text_label.pack()

            def on_click(event, frame=item_frame, path=full_path):
                self.select_item(frame, path)

            def on_double_click(event, path=full_path):
                if os.path.isdir(path):
                    self.load_folder(path)
                    self.push_history(path)
                else:
                    open_file_externally(path)

            def on_right_click(event, frame=item_frame, path=full_path):
                self.select_item(frame, path)
                self.show_context_menu_canvas(event)

            for widget in [item_frame, icon_label, text_label]:
                widget.bind("<Button-1>", on_click)
                widget.bind("<Double-1>", on_double_click)
                widget.bind("<Button-3>", on_right_click)

            col += 1
            if col >= columns:
                col = 0
                row += 1

        self.update_nav_buttons()
    def select_item(self, frame, path):
        if self.selected_item:
            old_frame, _ = self.selected_item
            old_frame.config(bg="white")
            for w in old_frame.winfo_children():
                w.config(bg="white")
        frame.config(bg="#cce6ff")
        for w in frame.winfo_children():
            w.config(bg="#cce6ff")
        self.selected_item = (frame, path)

    def show_context_menu_canvas(self, event):
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if not widget:
            return
        frame = widget
        while frame != self.inner_frame and frame is not None:
            if isinstance(frame, tk.Frame) and frame.master == self.inner_frame:
                break
            frame = frame.master
        else:
            return
        path = None
        if self.selected_item and self.selected_item[0] == frame:
            path = self.selected_item[1]
        else:
            for child in self.inner_frame.winfo_children():
                if child == frame:
                    labels = [w for w in child.winfo_children() if isinstance(w, tk.Label)]
                    if labels:
                        text = labels[-1].cget("text")
                        path = os.path.join(self.current_path, text)
                        self.select_item(frame, path)
                        break
        if not path:
            return
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="🗂 Open", command=lambda: self.open_selected_path(path))
        menu.add_command(label="📝 Rename", command=lambda: self.rename_path(path))
        menu.add_command(label="🗑 Delete", command=lambda: self.delete_path(path))
        menu.post(event.x_root, event.y_root)

    def push_history(self, path):
        if self.history_index >= 0 and self.history and self.history[self.history_index] == path:
            return
        self.history = self.history[:self.history_index + 1]
        self.history.append(path)
        self.history_index += 1
        self.update_nav_buttons()

    def update_nav_buttons(self):
        self.btn_back.config(state=tk.NORMAL if self.history_index > 0 else tk.DISABLED)
        self.btn_forward.config(state=tk.NORMAL if self.history_index < len(self.history) - 1 else tk.DISABLED)

    def go_back(self, event=None):
        if self.history_index > 0:
            self.history_index -= 1
            self.load_folder(self.history[self.history_index])
            self.update_nav_buttons()
    def go_forward(self, event=None):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_folder(self.history[self.history_index])
            self.update_nav_buttons()
    def on_search_enter(self, event=None):
        self.search_entry.selection_clear()
        self.search_items()
        self.canvas.focus_set()
    def handle_search_click(self):
        self.search_items()
        self.canvas.focus_set()
