import os
import hashlib


class Scanner:

    def __init__(self):

        self.threats = []


    def calculate_hash(self, file_path):

        sha256 = hashlib.sha256()

        try:

            with open(file_path, "rb") as file:

                while chunk := file.read(4096):

                    sha256.update(chunk)


            return sha256.hexdigest()

        except Exception:

            return None



    def scan_file(self, file_path):

        result = {
            "file": file_path,
            "status": "Safe",
            "hash": None
        }


        if os.path.exists(file_path):

            result["hash"] = self.calculate_hash(file_path)


            # Placeholder detection system
            suspicious_words = [
                "virus",
                "malware",
                "trojan"
            ]


            filename = file_path.lower()


            for word in suspicious_words:

                if word in filename:

                    result["status"] = "Threat Found"

                    self.threats.append(result)

                    break


        return result



    def get_threats(self):

        return self.threats