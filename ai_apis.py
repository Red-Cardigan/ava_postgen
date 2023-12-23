import openai
import requests

openai.api_key = 'your-api-key'

def generate_content(prompt):
    try:
        response = openai.Completion.create(
          engine="text-davinci-002",
          prompt=prompt,
          temperature=0.5,
          max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        raise Exception(f'Error in generating content: {str(e)}')

def generate_image(prompt):
    try:
        # Assuming DALL·E-3 API has a similar structure to OpenAI's GPT-3
        # Replace 'your-api-key' and 'your-endpoint-url' with actual API key and endpoint URL
        headers = {
            'Authorization': 'Bearer your-api-key',
            'Content-Type': 'application/json'
        }

        data = {
            'prompt': prompt,
            'max_tokens': 100
        }

        response = requests.post('your-endpoint-url', headers=headers, json=data)

        if response.status_code != 200:
            raise Exception(f'Error in generating image: {response.text}')

        return response.json()['image']
    except Exception as e:
        raise Exception(f'Error in generating image: {str(e)}')
