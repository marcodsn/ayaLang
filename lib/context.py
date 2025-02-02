import json
import os
from lib.user import User

class Context:
    DEFAULT_USER_SETTINGS = {
        "lang": "en",
        "romaji": False,
        "english": True,
        "formality": "normal"
    }

    def __init__(self):
        self.global_settings = self.load_global_settings()
        self.languages = self.load_languages()
        self.user_data_path = "lib/data/users"
        self.users = {}

    def load_global_settings(self):
        try:
            with open("settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: settings.json not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Invalid JSON in settings.json.")
            return {}

    def load_languages(self):
        try:
            with open("languages.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: languages.json not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Invalid JSON in languages.json.")
            return {}

    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = User(user_id, self)
        return self.users[user_id]

    def save_user(self, user_id):
        user = self.users.get(user_id)
        if user:
            user.save_settings()
            user.save_history()
