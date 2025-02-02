# ayaLang: Your AI Language Learning Companion

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

ayaLang is a Telegram bot designed to help you learn languages through engaging, AI-powered conversations. It acts as a virtual friend, providing a natural and interactive way to practice your target language.

## Features

*   **Multi-Language Support:** Learn English, Japanese, Italian, Spanish, French, Hindi, Brazilian Portuguese, Mandarin Chinese, and British English.
*   **Personalized Learning:** Customize your learning experience with adjustable settings like romaji display and English translation visibility.
*   **Contextual Conversations:** The bot maintains conversation history for more natural and meaningful interactions.
*   **Voice Output:** Hear the pronunciation of words and phrases in supported languages using the Kokoro Text-to-Speech engine.

## Supported Languages

| Language             | Command | Flag | Kokoro TTS |
| -------------------- | ------- | ---- | ---------- |
| English              | `/en`    | 🇬🇧   | Yes        |
| Japanese             | `/jp`    | 🇯🇵   | Yes        |
| Italian              | `/it`    | 🇮🇹   | Yes        |
| Spanish              | `/es`    | 🇪🇸   | Yes        |
| French               | `/fr`    | 🇫🇷   | Yes        |
| Hindi                | `/hi`    | 🇮🇳   | Yes        |
| Brazilian Portuguese | `/br`    | 🇧🇷   | Yes        |
| Mandarin Chinese     | `/zh`    | 🇨🇳   | Yes        |
| British English      | `/gb`    | 🇬🇧   | Yes        |

## Project Structure

```
.
├── lib
│ ├── __init__.py
│ ├── context.py
│ ├── data
│ │ └── users
│ ├── kokoro_tts.py
│ ├── openai_adapter.py
│ ├── prompts.py
│ └── telegram.py
│ └── user.py
├── main.py
├── requirements.txt
├── settings.json
└── languages.json
```

## Getting Started

### Prerequisites

*   Python 3.11 or higher
*   `pip`
*   Your Telegram Bot Token
*   Your OpenAI API Key (or a compatible model provider, e.g., ollama, tabbyAPI)
*   `espeak-ng` (for [Kokoro TTS](https://huggingface.co/hexgrad/Kokoro-82M))

Note: The suggested model for this project is [aya-expanse from Cohere](https://huggingface.co/CohereForAI/aya-expanse-32b)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/marcodsn/ayaLang.git
    cd ayaLang
    ```

2. **Install system dependencies:**

    ```bash
    sudo apt-get update && sudo apt-get install -y espeak-ng
    ```
3. **Create and activate a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4. **Install required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Configure Settings:**

    *   Rename `settings.example.json` to `settings.json`.
    *   Fill in your Telegram `bot_token` and `chat_ids` (whitelist of users who can use the bot).
    *   Configure your OpenAI settings:
        *   `base_url`: The base URL for the OpenAI API (or your compatible provider).
        *   `api_key`: Your OpenAI API key.
        *   `engine`: The name of the language model you want to use.

6. **Run the bot:**

    ```bash
    python main.py
    ```

## Usage

1. Start a chat with your Telegram bot.
2. Use the `/start` command to begin.
3. Select your desired language using the provided commands (e.g., `/jp` for Japanese).
4. Start chatting in your target language!

### Commands

*   `/start` - Start the bot and choose a language.
*   `/help` - Get help and instructions.
*   `/languages` - List available languages.
*   `/settings` - View your current settings.
*   `/set <setting> <value>` - Change a setting (e.g., `/set romaji true`).
*   `/listen` - Generate a TTS audio of the last bot message (If available for the language).
*   `/clear` - Clear your conversation history.
*   `/<language_code>` - Switch to a specific language (e.g., `/it`, `/es`, `/fr`).

## Thanks

*   [Hexgrad](https://huggingface.co/hexgrad) for their incredible work on Kokoro.
*   [Cohere](https://cohere.com/) for providing an amazing multi-lingual model.

## License

Copyright 2025 \[Marco De Santis]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
