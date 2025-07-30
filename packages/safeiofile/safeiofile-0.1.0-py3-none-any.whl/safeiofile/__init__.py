import os
from datetime import datetime

class File:
    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def write(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(data)
        return self

    def append(self, data):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(data + "\n")
        return self

    def backup(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.path}.{ts}.bak"
        with open(self.path, "rb") as src, open(backup_path, "wb") as dst:
            dst.write(src.read())
        return backup_path

    def rotate_if_large(self, max_mb=1):
        size_mb = os.path.getsize(self.path) / (1024 * 1024)
        if size_mb > max_mb:
            self.backup()
            self.write("")  # truncate
        return self
