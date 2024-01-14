import openai
import requests
from openai import OpenAI
from flask import Flask, request
import ai_apis

app = Flask(__name__)

openai.api_key = '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' #My Key
client = openai.OpenAI(api_key=openai.api_key)

# @app.route('/api/generate', methods=['POST'])
# def generate():
#     data = request.get_json()
#     response = ai_apis.gpt_call(data['prompt'], data['model'])
#     return response

def gpt_call(prompt, model):
    # This needs to be adjusted to retrieve context from Ava_entire.pdf
    try:
        # "gpt-4-1106-preview"
        response = client.chat.completions.create(
          model=model,
          prompt=prompt,
          temperature=0,
          max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f'Error in generating content: {str(e)}')

def generate_image(prompt):
    try:
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'prompt': prompt,
            'max_outputs': 1
        }

        response = requests.post('https://api.openai.com/v1/images', headers=headers, json=data)

        if response.status_code != 200:
            raise Exception(f'Error in generating image: {response.text}')

        return response.json()['outputs'][0]['image']
    except Exception as e:
        raise Exception(f'Error in generating image: {str(e)}')
