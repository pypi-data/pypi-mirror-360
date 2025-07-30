import json
import requests
from dotenv import load_dotenv
import os
import json
from services.constants import experiment_system_input, original_system_input

class ChatGPT4Service:
    def __init__(self):
        print("Chat GPT 4")
        load_dotenv()
        self.API_KEY = os.getenv("AI_ML_API_VALUE")

    def _get_user_input(self, html, feature_scenario, text_line):
        return f"""
        LINE OF FEATURE SCENARIO:
        {text_line}.

        HTML_code: 
        {html}

        FEATURE SCENARIO: 
        {feature_scenario}
        """


    def generate(self, html, feature_scenario, text_line):
        user_input = self._get_user_input(html, feature_scenario, text_line)
        whole_input = f"System input: {experiment_system_input}, \n\nuser_input: {user_input}"


        response = requests.post(
            "https://api.aimlapi.com/chat/completions",
            headers={"Content-Type":"application/json", "Authorization": f"Bearer {self.API_KEY}"},
            json={"model": "gpt-4",
            "messages":[
                {"role": "user", "content": whole_input},
                {"role": "assistant", "content": '[NO PROSE]'}
                ]}
        )
        print(response.json().get("choices")[0].get("message").get("content"))
        response_text = response.json().get("choices")[0].get("message").get("content")

        data = response_text
        data = data.replace("```json", "")
        data = data.replace("```", "")

        json_data = json.loads(data)
        python_script = json_data

        print(data)
        return python_script
