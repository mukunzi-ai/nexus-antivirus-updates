class AIDetector:


    def __init__(self):

        self.suspicious_extensions = [
            ".exe",
            ".bat",
            ".cmd",
            ".vbs"
        ]


        self.suspicious_names = [
            "virus",
            "malware",
            "trojan",
            "hack",
            "keylogger"
        ]



    def analyze(self, file_path):

        score = 0
        reasons = []


        file_name = file_path.lower()


        # Check extension
        for ext in self.suspicious_extensions:

            if file_name.endswith(ext):

                score += 20

                reasons.append(
                    "Executable file"
                )



        # Check suspicious words
        for word in self.suspicious_names:

            if word in file_name:

                score += 70

                reasons.append(
                    f"Suspicious name: {word}"
                )



        if score >= 70:

            status = "Dangerous"

        elif score >= 30:

            status = "Suspicious"

        else:

            status = "Safe"



        return {

            "score": score,

            "status": status,

            "reasons": reasons

        }
