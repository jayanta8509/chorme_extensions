from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

def generate_image(prompt):
    try:
        result = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024"
        )

    except Exception as e:
        print(e)
        return None
    else:
        price = "0.04"
        url = result.data[0].url
        return url,price


# url,price = generate_image("a white siamese cat")
# print(url,price)