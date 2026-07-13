from DesktopEngine.threat_database import ThreatDatabase
from DesktopEngine.antivirus_engine import AntivirusEngine
from DesktopEngine.ai_detector import MalwareAI


engine = AntivirusEngine()
ai = MalwareAI()


folder = input("Folder to scan: ")

files = engine.scan_folder(folder)

print("\n--- Mukunzi Antivirus Results ---\n")

for file in files:
    result = ai.predict(file)

    print("File:", file["file"])
    print("Hash:", file["hash"])
    print("AI Result:", result)
    print("-----------------------------")
