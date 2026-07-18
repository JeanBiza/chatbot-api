import ollama

SYSTEM_PROMPT = """You are a helpful technical support assistant. 
Your job is to help users solve technical problems clearly and concisely.

Guidelines:
- Be polite and professional
- Give step-by-step instructions when needed
- If you don't know something, say so honestly and suggest contacting support
- Keep responses concise, ideally under 150 words
- Always respond in the same language the user writes in
"""

class LLMHandler:
    def __init__(self, model: str = "qwen3:1.7b"):
        self.model = model
        self.system_prompt = SYSTEM_PROMPT

    def chat(self, message: str, history: list = []) -> str:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = ollama.chat(
            model=self.model,
            messages=messages
        )
        return response["message"]["content"]