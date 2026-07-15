import os
import json
import shutil
import uuid
from datetime import datetime


class QuarantineManager:

    def __init__(self):

        self.quarantine_folder = "Quarantine"
        self.database_file = "data/quarantine.json"

        os.makedirs(self.quarantine_folder, exist_ok=True)
        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.database_file):

            with open(self.database_file, "w") as f:
                json.dump({}, f, indent=4)

    def load_database(self):

        with open(self.database_file, "r") as f:
            return json.load(f)

    def save_database(self, data):

        with open(self.database_file, "w") as f:
            json.dump(data, f, indent=4)

    def quarantine(self, filepath, reason="Unknown Threat"):

        if not os.path.exists(filepath):
            return False

        unique_id = str(uuid.uuid4())

        filename = os.path.basename(filepath)

        destination = os.path.join(
            self.quarantine_folder,
            unique_id
        )

        shutil.move(filepath, destination)

        db = self.load_database()

        db[unique_id] = {

            "original_name": filename,

            "original_path": filepath,

            "reason": reason,

            "quarantined_at":
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }

        self.save_database(db)

        return True

    def restore(self, unique_id):

        db = self.load_database()

        if unique_id not in db:
            return False

        source = os.path.join(
            self.quarantine_folder,
            unique_id
        )

        destination = db[unique_id]["original_path"]

        os.makedirs(
            os.path.dirname(destination),
            exist_ok=True
        )

        shutil.move(source, destination)

        del db[unique_id]

        self.save_database(db)

        return True

    def delete(self, unique_id):

        db = self.load_database()

        if unique_id not in db:
            return False

        source = os.path.join(
            self.quarantine_folder,
            unique_id
        )

        if os.path.exists(source):
            os.remove(source)

        del db[unique_id]

        self.save_database(db)

        return True

    def list_files(self):

        return self.load_database()
