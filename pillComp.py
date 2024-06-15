import base64
import requests
import os

# OpenAI API Key
api_key = os.getenv('OPEN_API_KEY')


headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4o",
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": """ I will give you several pills.  You're an expert pharmacist. For each pill in the list 
          provided you will explain the side effects that a user may experience when taking this pill with any other pill in the list. 
          If there are any side effects with any of the pills being taken together, state clearly and concicesly what those are. If the pills can be taken together without side effects, respond 'These pills can be 
          taken together without any major health concerns.  
          After you have the statements rewrite the above statements eliminating any descriptive detail. Keep it simply the side effects for each pill combination.
          Please return this as HTML span.
          """
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "The pills are trazidone, nyquil and amoxicillin."
        },
      ]
    }
  ],
  "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())