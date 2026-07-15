import json
import os


class ThreatDatabase:
    """
    Nexus Beta Threat Database
    --------------------------
    Stores and searches known malware hashes.
    """

    def __init__(self):

        self.database_path = "data/threats.json"

        os.makedirs("data", exist_ok=True)

        if not os.path.exists(self.database_path):

            with open(self.database_path, "w") as file:

                json.dump({}, file, indent=4)

    def load(self):

        try:

            with open(self.database_path, "r") as file:

                return json.load(file)

        except Exception:

            return {}

    def save(self, database):

        with open(self.database_path, "w") as file:

            json.dump(database, file, indent=4)

    def check_hash(self, sha256):

        database = self.load()

        return database.get(sha256)

    def add_threat(

        self,

        sha256,

        name,

        risk,

        category="Unknown",

        description=""

    ):

        database = self.load()

        database[sha256] = {

            "name": name,

            "risk": risk,

            "category": category,

            "description": description

        }

        self.save(database)

    def remove_threat(self, sha256):

        database = self.load()

        if sha256 in database:

            del database[sha256]

            self.save(database)

    def list_threats(self):

        return self.load()
