from openai import OpenAI
from lib.prompts import get_prompt

class Model:
    def __init__(self, user):
        self.user = user
        try:
            self.client = OpenAI(
                base_url=user.context.global_settings["openai"]["base_url"],
                api_key=user.context.global_settings["openai"]["api_key"]
            )
        except KeyError as e:
            raise ValueError(f"Missing OpenAI configuration: {e}")
        except Exception as e:
            raise ValueError(f"Error initializing OpenAI client: {e}")

    def answer(self, message):
        try:
            response = self.client.chat.completions.create(
                model=self.user.context.global_settings["openai"]["engine"],
                messages=[
                    {"role": "system", "content": get_prompt(self.user.settings["lang"], self.user)},
                    *self.user.history,
                    {"role": "user", "content": message}
                ],
            )
            if not response.choices:
                raise ValueError("Empty response from OpenAI API")

            answer = response.choices[0].message.content
            # Extract JSON string (assuming the model always returns JSON within markdown)
            answer = answer.split("```json")[1].split("```")[0].strip()

            self.user.add_message("user", message) # Add user message to history after successful API call
            self.user.add_message("assistant", "```json\n" + answer + "```")
            self.user.save_history()
            return answer

        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            raise
