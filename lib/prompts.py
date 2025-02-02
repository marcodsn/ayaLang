def get_prompt(lang="en", user=None):
    context = user.context if user else None

    if context and lang in context.languages:
        prompt = context.languages[lang]["prompt"]

        if user and user.settings.get("formality") == "very_casual":
            prompt += "\n\nAlso, please use a very casual and friendly tone, like close friends."

        persona = "Your name Aya, a friendly and helpful AI."
        prompt = f"{prompt}\n\n{persona}"

        return prompt

    return ""  # Default empty prompt
