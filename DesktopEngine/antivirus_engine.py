import hashlib
import os
from pathlib import Path
from datetime import datetime


class AntivirusEngine:
    """
    Nexus Beta Antivirus Engine
    ----------------------------
    Responsible for:
        • Scanning folders
        • Collecting file information
        • Calculating SHA-256 hashes
    """

    def __init__(self):
        self.supported_extensions = [
            ".exe",
            ".dll",
            ".sys",
            ".bat",
            ".cmd",
            ".com",
            ".scr",
            ".msi",
            ".jar",
            ".vbs",
            ".ps1",
            ".zip",
            ".rar",
            ".7z",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx"
        ]

    def calculate_hash(self, filepath):
        """Return SHA-256 hash."""

        sha256 = hashlib.sha256()

        try:

            with open(filepath, "rb") as file:

                while True:

                    data = file.read(4096)

                    if not data:
                        break

                    sha256.update(data)

            return sha256.hexdigest()

        except Exception:

            return "HASH_ERROR"

    def get_file_information(self, filepath):

        path = Path(filepath)

        try:

            size = os.path.getsize(filepath)

            modified = datetime.fromtimestamp(
                os.path.getmtime(filepath)
            )

        except Exception:

            size = 0

            modified = datetime.now()

        return {

            "file": str(path),

            "name": path.name,

            "extension": path.suffix.lower(),

            "size": size,

            "modified": modified.strftime("%Y-%m-%d %H:%M:%S"),

            "hash": self.calculate_hash(filepath),

        }

    def should_scan(self, filepath):

        extension = Path(filepath).suffix.lower()

        if extension in self.supported_extensions:

            return True

        return False

    def scan_folder(self, folder):

        results = []

        if not os.path.exists(folder):

            return results

        for root, dirs, files in os.walk(folder):

            for filename in files:

                filepath = os.path.join(root, filename)

                if self.should_scan(filepath):

                    info = self.get_file_information(filepath)

                    results.append(info)

        return results
