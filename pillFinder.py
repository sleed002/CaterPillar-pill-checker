import base64
import requests
import os

# OpenAI API Key
api_key = os.getenv('OPEN_API_KEY')

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_test_1= "./uploads/samples/traz3.jpeg"
image_test_2= "./uploads/samples/amox.png"
image_test_3= "./uploads/samples/dip.jpeg"
image_test_4= "./uploads/samples/lor.jpeg"
image_coll = "./uploads/samples/coll1.jpeg"

# Getting the base64 string
base64_image_shelf = encode_image(image_coll)
base64_image_product = encode_image(image_test_3)

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
          "text": "First, I will give you an image of a pill. Then i will give you an image of a collection of pills in a container. Your task is to tell me if the pill is in the collection of pills, and what quadrant of the picture it is in."
        }
      ]
    },
  {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Here is the product image"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image_product}"
          }
        }
    ]
  },
{
    "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Here is the aisle image"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image_shelf}"
          }
        }
      ]
    }
  ],
  "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())