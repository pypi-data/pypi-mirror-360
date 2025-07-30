import os
import shutil

class FolderManager:
    def create_folder(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)
    
    def delete_folder(self, path: str) -> None:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    def list_files(self, path: str, extension_filter: str = None) -> list:
        if not os.path.exists(path):
            return []
        files = os.listdir(path)
        return [f for f in files if f.endswith(extension_filter)] if extension_filter else files
    
    def copy_file(self, src: str, dest: str) -> None:
        if os.path.isfile(src):
            shutil.copy(src, dest)
    
    def move_file(self, src: str, dest: str) -> None:
        if os.path.isfile(src):
            shutil.move(src, dest)
