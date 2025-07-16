# main.py
import tkinter as tk
import gui_helpers
from file_explorer_core import FileExplorerApp  # Updated import

def main():
    root = tk.Tk()
    gui_helpers.load_icons(root)  # Load icons AFTER root creation
    app = FileExplorerApp(root, gui_helpers.folder_icon, gui_helpers.search_icon)
    root.mainloop()

if __name__ == "__main__":
    main()

