import shutil
from pathlib import Path
from importlib.resources import files
from . import GUI

def get_examlpes(target_dir="pytac3d_examples"):
    examples_dir = files('PyTac3D') / 'example'
    target_path = Path(target_dir)
    
    if target_path.exists():
        raise FileExistsError(f"Folder exists: {target_path}")
    
    shutil.copytree(str(examples_dir), target_path)
    print(f"Examples are copied to : {target_path.absolute()}")

def run_pytac3d_gui():
    window = GUI.MainWindow()
    window.run()
    window.stop()