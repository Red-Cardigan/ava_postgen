import openai
import requests
from openai import OpenAI
import logging
import json
import time

openai.api_key = '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' #My Key
client = openai.OpenAI(api_key=openai.api_key)

prompt = "Ava's first experience on a plane"
model = "gpt-3.5-turbo-1106"

with open('prompts.json', 'r') as f:
    data = json.load(f)

notes_1_ft = data['NOTES_1_FT']
    
file = client.files.create(
  file=open("Ava_entire.pdf", "rb"),
  purpose='assistants'
)

def thread(prompt):
  assistant = client.beta.assistants.create(
        instructions=f"Provide clear and detailed notes on {prompt}",
        model="gpt-3.5-turbo-1106",
        tools=[{"type": "retrieval"}],
        file_ids=[file.id]
    )
  thread = client.beta.threads.create(
    messages=[
        {
        "role": "user",
        "content": f"Provide clear and detailed notes on {prompt}",
        "file_ids": [file.id]
        }
      ]
  )
  # print(thread)
  run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
      model="gpt-3.5-turbo-1106",
      # instructions=notes_1_ft,
  )
  
  run_ = {}
  run_['status'] = ''
  run_['thread_id'] = run.thread_id
  run_['id'] = run.id
  while run_['status'] != "completed":
    time.sleep(1)
    response = requests.get(
        f"https://api.openai.com/v1/threads/{run_['thread_id']}/runs/{run_['id']}",
        headers={
            "Authorization": f"Bearer {openai.api_key}",
            "OpenAI-Beta": "assistants=v1"
        }
    )
    run_ = response.json()
  print(run_)

  response_messages = requests.get(
    f"https://api.openai.com/v1/threads/{run_['thread_id']}/messages",
    headers={
        "Authorization": f"Bearer {openai.api_key}",
        "OpenAI-Beta": "assistants=v1"
    }
  )
  messages = response_messages.json()
  for message in messages['data']:
    print(message['content'][0]['text']['value'])

  # print(client.beta.threads.messages(thread_id=thread.id))
  # response = client.beta.threads.messages(thread_id=thread.id).data[-1]
  # print(response)
  # print(client.beta.threads.messages.list(thread_id=thread.id))
  # print(client.beta.threads.messages.list(thread_id=thread.id).data)
  # print(response.dict())
  # return response.dict()
    
# def gpt_call(prompt, model):
#     # This needs to be adjusted to retrieve context from Ava_entire.pdf
#     try:
#         # "gpt-4-1106-preview"
#         response = client.chat.completions.create(
#           model=model,
#           messages=[prompt],
#           temperature=0,
#           max_tokens=2000
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         raise Exception(f'Error in generating content: {str(e)}')
    
# gpt_call(prompt, model)
thread(prompt)