import os
import shutil
from tkinter import simpledialog

def build_tree_recursive(tree, path, parent):
    try:
        entries = os.listdir(path)
    except PermissionError:
        return
    for entry in entries:
        full_path = os.path.join(path, entry)
        node = tree.insert(parent, "end", text=entry, open=False)
        if os.path.isdir(full_path):
            build_tree_recursive(tree, full_path, node)

def search_recursive(tree):
    name = simpledialog.askstring("Search", "Enter file or folder name:")
    if not name:
        return

    def recursive_search(node):
        text = tree.item(node, "text")
        if name.lower() in text.lower():
            tree.selection_add(node)
            tree.see(node)
        for child in tree.get_children(node):
            recursive_search(child)

    tree.selection_remove(tree.selection())
    for root_node in tree.get_children():
        recursive_search(root_node)

def delete_path(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True
    except Exception as e:
        print(f"Delete error: {e}")
        return False

def move_path(source, destination_folder):
    try:
        abs_source = os.path.abspath(source)
        abs_destination = os.path.abspath(destination_folder)
        # Prevent moving folder into itself or its subfolder
        if abs_destination.startswith(abs_source):
            return False
        shutil.move(source, destination_folder)
        return True
    except Exception as e:
        print(f"Move error: {e}")
        return False
