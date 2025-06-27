import requests

from myutils.logging import gotenv


class EasyLlama:

    def __init__(self, sys_prompt: str, model: str = 'codellama') -> None:

        self.messages = [{'role': 'system', 'content': sys_prompt}]
        self.api = gotenv('OLLAMA_API')
        self.model = model

    def send(self, message: str) -> str:

        # Append message to message list
        self.messages.append({'role': 'user', 'content': message})

        # Construct payload
        payload = {
            'model': self.model,
            'messages': self.messages,
            'stream': False
        }

        # Get the response
        response = requests.post(
            f"{self.api}/chat",
            json=payload
        )

        print(response.json())

        # Return the text response
        return response.json()['message']['content']
