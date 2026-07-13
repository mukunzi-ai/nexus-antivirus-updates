class MalwareAI:

    def predict(self, file_data):

        score = 0

        extension = file_data["extension"]
        size = file_data["size"]

        dangerous_extensions = [
            ".exe",
            ".dll",
            ".sys",
            ".bat",
            ".cmd",
            ".scr",
            ".vbs",
            ".ps1"
        ]

        if extension in dangerous_extensions:
            score += 30

        if size > 50 * 1024 * 1024:
            score += 10

        if score >= 70:

            prediction = "Malicious"

        elif score >= 30:

            prediction = "Suspicious"

        else:

            prediction = "Safe"

        return {

            "prediction": prediction,

            "confidence": score

        }
