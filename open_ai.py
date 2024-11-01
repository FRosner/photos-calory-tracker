import os

import base64

from openai import OpenAI


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image


image_path = "/Users/frosner/tmp/frosner.jpg"
encoded_image = encode_image(image_path)

client = OpenAI(
    api_key=os.getenv("FROODS_OPENAPI_KEY")
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What is in this image?",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]
        }
    ],
    model="gpt-4o-mini",
)

print(chat_completion)
