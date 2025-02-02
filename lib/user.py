import json
import os

class User:
    def __init__(self, user_id, context):
        self.user_id = user_id
        self.context = context
        self.settings = self.load_settings()
        self.history = self.load_history()

    def load_settings(self):
        filepath = os.path.join(self.context.user_data_path, str(self.user_id), "settings.json")
        try:
            with open(filepath, "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = self.context.DEFAULT_USER_SETTINGS.copy()
            self.save_settings(settings)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in settings file for user {self.user_id}.")
            settings = self.context.DEFAULT_USER_SETTINGS.copy()

        return settings

    def save_settings(self, settings=None):
        if settings is None:
            settings = self.settings
        filepath = os.path.join(self.context.user_data_path, str(self.user_id), "settings.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        try:
            with open(filepath, "w") as f:
                json.dump(settings, f, indent=4)
        except (TypeError, OSError) as e:
            print(f"Error: Could not save settings for user {self.user_id}: {e}")

    def load_history(self):
        lang = self.settings["lang"]
        filepath = os.path.join(self.context.user_data_path, str(self.user_id), "history", f"{lang}.json")
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in history file for user {self.user_id}, language {lang}.")
            return []

    def save_history(self):
        lang = self.settings["lang"]
        filepath = os.path.join(self.context.user_data_path, str(self.user_id), "history", f"{lang}.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        try:
            with open(filepath, "w") as f:
                json.dump(self.history, f, indent=4)
        except (TypeError, OSError) as e:
            print(f"Error: Could not save history for user {self.user_id}, language {lang}: {e}")

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        self.save_history()

    def clear_history(self):
        self.history = []
        self.save_history()
