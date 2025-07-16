# gui_helpers.py
from PIL import Image, ImageTk#type:ignore
import os
import platform
import subprocess

folder_icon = None
file_icon = None
extension_icons = {}
search_icon = None

def load_icons(master):
    global folder_icon, file_icon, extension_icons, search_icon

    folder_img = Image.open(os.path.join("icons", "folder.png")).resize((32,32))
    folder_icon = ImageTk.PhotoImage(folder_img, master=master)

    file_img = Image.open(os.path.join("icons", "file.png")).resize((32,32))
    file_icon = ImageTk.PhotoImage(file_img, master=master)

    search_img = Image.open(os.path.join("icons", "search.png")).resize((20,20))
    search_icon = ImageTk.PhotoImage(search_img, master=master)

    extension_icons = {}

    def load_icon_for_extension(ext, icon_file):
        try:
            img_path = os.path.join("icons", icon_file)
            img = Image.open(img_path).resize((32,32))
            extension_icons[ext.lower()] = ImageTk.PhotoImage(img, master=master)
        except Exception as e:
            print(f"Failed to load icon {icon_file}: {e}")

    # Load icons for specific extensions - make sure these files exist inside the icons folder
    load_icon_for_extension('.txt', 'text.png')
    load_icon_for_extension('.py', 'py.png')
    load_icon_for_extension('.pdf', 'pdf.png')
    load_icon_for_extension('.jpg', 'image.png')
    load_icon_for_extension('.mp3', 'mp3.png')
    load_icon_for_extension('.mp4', 'video.png')
    load_icon_for_extension('.exe', 'exe.png')
    load_icon_for_extension('.docx', 'docx.png')
    
    # You can add more extensions here if needed

def get_icon_for_file(path):
    global file_icon, extension_icons
    _, ext = os.path.splitext(path)
    return extension_icons.get(ext.lower(), file_icon)

def open_file_externally(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])
