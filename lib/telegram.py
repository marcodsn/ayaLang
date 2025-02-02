import json
import os
import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters, MessageHandler
from lib.openai_adapter import Model
from lib.kokoro_tts import generate_tts
from telegram.error import TelegramError

class AyaLangBot:
    def __init__(self, context):
        self.context = context
        self.token = context.global_settings.get("telegram", {}).get("bot_token")
        if not self.token:
            raise ValueError("Telegram bot token is not set in settings.json")
        self.whitelist = context.global_settings.get("telegram", {}).get("whitelist")
        self.chat_ids = context.global_settings.get("telegram", {}).get("chat_ids")
        self.app = ApplicationBuilder().token(self.token).build()
        self.last_bot_message = {}

        # Handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("languages", self.languages))
        self.app.add_handler(CommandHandler("settings", self.show_settings))
        self.app.add_handler(CommandHandler("set", self.set_setting))
        self.app.add_handler(CommandHandler("listen", self.listen))
        self.app.add_handler(CommandHandler("clear", self.clear_history))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat))

        # Dynamically create language commands
        for lang_code in self.context.languages.keys():
            self.app.add_handler(CommandHandler(lang_code, self.set_language_command))

    async def set_language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        command = update.message.text[1:]  # Extract command without "/"
        if command in self.context.languages:
            await self.set_language(update, command, self.context.languages[command]["greeting"])
        else:
            await update.message.reply_text(f"Invalid language code: {command}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        user = self.context.get_user(user_id)
        lang_options = "\n".join([
            f"  - {self.context.languages[lang]['flag']} {lang.upper()}: /{lang}"
            for lang in self.context.languages if not self.context.languages[lang]["support"]
        ])
        await update.message.reply_text(
            f"""🤖 Welcome to ayaLang, your friendly AI language assistant!

To start, select a language you want to learn:
{lang_options}

Your current language is: {user.settings['lang']}

⚙️ /settings - View your settings.
✏️ /set - Change your settings.
❓ /help - Get help using the bot.
🗑️ /clear - Clear your chat history."""
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        await update.message.reply_text(
            """📚 ayaLang Bot Guide:

/help - Show this guide.
/languages - List available languages.
/settings - View your current settings.
/set <setting> <value> - Change a setting (e.g., /set romaji true).
/listen - Generate a TTS audio of the last bot message (If available for the language).
/clear - Clear your chat history.

💬 Just send a text message to chat with the bot in the selected language!"""
        )

    async def set_language(self, update: Update, lang: str, reply_text: str):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        user = self.context.get_user(user_id)
        user.settings["lang"] = lang
        user.clear_history()
        self.context.save_user(user_id)
        await update.message.reply_text(reply_text)

    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this bot.")
        user = self.context.get_user(user_id)
        model = Model(user)
        print(f"{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Message from {user_id}")

        try:
            response = model.answer(update.message.text)
            formatted_message = self.format_message(response, user.settings)
            self.last_bot_message[user_id] = response
            await update.message.reply_text(formatted_message)
        except Exception as e:
            print(f"Error in chat: {e}")
            await update.message.reply_text("Sorry, there was an error processing your message.")

    def format_message(self, response_json, settings):
        try:
            response = json.loads(response_json)
            message_parts = []
            lang = settings["lang"]

            if lang in self.context.languages:
                lang_data = self.context.languages[lang]
                flag = lang_data.get("flag", "🏳️")

                # Iterate over possible language keys from languages.json
                for lang_code, lang_info in self.context.languages.items():
                    if lang_info["language"] in response:
                        key = lang_info["language"]

                        # Show if it's the selected language or if it's English and English is enabled
                        if key == "english" and settings.get("english"):
                            message_parts.append(f"{lang_info.get('flag', '🏳️')} {response[key]}")
                        elif key == "romaji" and settings.get("romaji") and response.get(key):
                            message_parts.append(f"🔤 {response[key]}")
                        else:
                            message_parts.append(f"{lang_info.get('flag', '🏳️')} {response[key]}")

            return "\n\n".join(message_parts)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error formatting message: {e}")
            return "There was an error processing the response."

    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        user = self.context.get_user(user_id)
        settings_str = "\n".join(f"{key}: {value}" for key, value in user.settings.items())
        await update.message.reply_text(f"⚙️ Your current settings:\n{settings_str}")

    async def set_setting(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        user = self.context.get_user(user_id)

        try:
            parts = update.message.text.split()
            if len(parts) != 3:
                raise ValueError("Invalid number of arguments")

            key, value = parts[1], parts[2]
            if key not in user.settings:
                await update.message.reply_text(f"❌ Unknown setting '{key}'")
                return

            if key in ["romaji", "english"]:
                if value.lower() not in ["true", "false"]:
                    await update.message.reply_text(f"❌ Invalid value for '{key}'. Please use 'true' or 'false'.")
                    return
                value = value.lower() == "true"

            user.settings[key] = value
            self.context.save_user(user_id)
            await update.message.reply_text(f"✅ Setting '{key}' updated to '{value}'")

        except ValueError:
            await update.message.reply_text("Invalid format. Use /set <setting_name> <value>")
        except Exception as e:
            await update.message.reply_text(f"An unexpected error occurred: {e}")

    async def listen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        user = self.context.get_user(user_id)

        if user_id not in self.last_bot_message:
            await update.message.reply_text("❌ No message to generate audio from.")
            return

        try:
            response = json.loads(self.last_bot_message[user_id])
        except json.JSONDecodeError:
            await update.message.reply_text("❌ Error: Could not decode the last message.")
            return

        lang = user.settings["lang"]
        if lang not in self.context.languages:
            await update.message.reply_text(f"❌ Audio generation not supported for {lang}.")
            return

        kokoro_settings = self.context.languages[lang].get("kokoro")
        if not kokoro_settings:
            await update.message.reply_text(f"❌ Kokoro TTS not configured for {lang}.")
            return

        lang_code = kokoro_settings["lang_code"]
        voice = kokoro_settings["voices"].get(user.settings.get("voice", "default"), kokoro_settings["voices"]["default"])

        # Find the language-specific text to generate audio from
        text_key = None
        if lang == "jp":
            text_key = "japanese"
        elif lang == "it":
            text_key = "italian"
        elif lang == "es":
            text_key = "spanish"
        elif lang == "fr":
            text_key = "french"
        elif lang == "hi":
            text_key = "hindi"
        elif lang == "br":
            text_key = "brazilian"
        elif lang == "zh":
            text_key = "chinese"
        elif lang == "gb":
            text_key = "british"
        elif lang == "en":
            text_key = "english"

        if text_key is None or text_key not in response:
            await update.message.reply_text(f"❌ Could not find appropriate text for audio generation in {lang}.")
            return

        text_to_speak = response[text_key]

        try:
            audio_file = generate_tts(text_to_speak, lang_code, voice)
            with open(audio_file, 'rb') as audio:
                await update.message.reply_voice(voice=audio)
        except TelegramError as e:
            print(f"Telegram error during audio send: {e}")
            await update.message.reply_text(f"Error sending audio: {e}")
        except Exception as e:
            print(f"Error generating or sending audio: {e}")
            await update.message.reply_text(f"Error generating audio: {e}")
        finally:
            if 'audio_file' in locals() and os.path.exists(audio_file):
                os.remove(audio_file)

    async def languages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        lang_list = "\n".join([
            f"/{lang_code.lower()} - {lang_data['language']}"
            for lang_code, lang_data in self.context.languages.items() if not lang_data["support"]
        ])
        await update.message.reply_text(f"🌍 Available languages:\n{lang_list}")

    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if str(user_id) not in self.chat_ids and self.whitelist:
            print(f"User {user_id} not in chat_ids and whitelist is enabled")
            await update.message.reply_text("You are not authorized to use this command.")
        user = self.context.get_user(user_id)
        user.clear_history()
        await update.message.reply_text("🗑️ Chat history cleared.")

    def run(self):
        self.app.run_polling()
