
import os
import subprocess
import platform

def open_app_data_folder():
    """Uygulamanın AppData/Roaming/mstpull klasörünü sistem dosya yöneticisinde açar."""
    app_data = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'mstpull')
    os.makedirs(app_data, exist_ok=True)
    
    if platform.system() == "Windows":
        os.startfile(app_data)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", app_data])
    else:
        subprocess.Popen(["xdg-open", app_data])
