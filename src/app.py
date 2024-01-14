from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
# from database import add_content_to_db
from flask_cors import CORS
from flask import Response
from flask_sse import sse

import openai
import requests
from openai import OpenAI
import logging
import json
import time
import requests

app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost:6379"
app.register_blueprint(sse, url_prefix='/stream')

openai.api_key = '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' #My Key
client = openai.OpenAI(api_key=openai.api_key)
# tavily_api_key = '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' For research gpt 

# with open('prompts.json', 'r') as f:
#     data = json.load(f)

# notes_1_ft = data['NOTES_1_FT']

# logging.getLogger('flask_cors').level = logging.DEBUG
# logging.basicConfig(filename='response_headers.log', level=logging.INFO)


# CORS(app, resources={r"/api/*": {"origins": "*"}})
# cors = CORS(app, resources={r"/*": {"origins": ["http://localhost:5000", "http://localhost:3000"]}})
# app.config['CORS_HEADERS'] = 'Content-Type'

#Run once when you launch the server then COMMENT OUT
# file = client.files.create(
#     file=open("Ava_entire.pdf", "rb"),
#     purpose='assistants'
# )
# print('file added')


######CREATE NOTE WRITING ASSISTANT######
# assistant = client.beta.assistants.create(
#     instructions=f"""
# Act as Ava, the character in the story provided in context. You're an incredibly intelligent and detail-oriented woman who's an expert in software, natural sciences, and engineering.

# Use relevant context to provide structured bullet-point notes for a post on your science blog. Share insights about the human mind and society using your experiences. Focus on events, people, and facts rather than yourself. Include additional scientific context where relevant. Follow these steps:

# 1) Structure: Devise an engaging structure for your post which conveys an insight about human mind and/or society.
# 2) Pacing: Detail how you'll expertly use varied pacing to carry the message.
# 3) Narrative Tone: Consider a balance of serious and humorous to keep the reader engaged. Contrast negative and positive aspects to draw a mature conclusion.
# 4) Use of Language: Provide specific detail on how you'll use vocabulary, punctuation, and sentence structure to add depth and character.
# # """,
#     # model="gpt-4-1106-preview",
#     model = "gpt-4-1106-preview",
#     tools=[{"type": "retrieval"}],
#     file_ids=[file.id]
# )
# print(f'assistant added with id: {assistant.id}')
# assistant_id = assistant.id
#####################################

# Act as Ava, the character in the story provided in context. You're an incredibly intelligent and detail-oriented woman who's an expert in software, natural sciences, and engineering. You're very curious and yet cautious about humanity, and care deeply for others despite their flaws. You're writing to justify your actions in light of unspecified major world events. 

# Use the provided context to write well-structured bullet-point notes for your science blog, where you share your experiences alongside insights about the human mind and society. Focus on events, other people, and scientific facts rather than yourself. Provide additional scientific context where relevant. 

# Structure: Devise an engaging structure for your post. 
# Pacing: Detail expert use of varied pacing 
# Narrative Tone:  (serious, humorous, etc.) to keep the reader engaged. You should contrast negative and positive aspects to draw mature conclusions.
# Narrative Techniques: Provide specific detail on how vocabulary, punctuation, and sentence structure will be used to add depth and character.

######CREATE FEEDBACK ASSISTANT######
# assistant = client.beta.assistants.create(
#     instructions=f"""
# Use your notes on pacing, narrative tone, and use of language to provide more developed notes, adding new details, carefully interwoven explanations of technical concepts, and expanding on descriptions of characters and places. 
# """,
#     # model="gpt-4-1106-preview",
#     model = "gpt-4-1106-preview",
#     tools=[{"type": "retrieval"}],
#     file_ids=[file.id]
# )
# print(f'assistant added with id: {assistant.id}')
# assistant_2_id = assistant.id
#####################################



# print(f"File ID: {file.id}\n Assistant ID: {assistant_id}")
# file_id = "file-8e5O2OHOAYxc7teoLwVniT1B"


######REFRESH ASSISTANT FILE#######
assistant_id = "asst_DsoiC4TAYHztKtBfyi1erKzd"
file_id = "file-uk3vfoPNItOdsiRxDxHujqUN"
url = f"https://api.openai.com/v1/assistants/{assistant_id}/files"
headers = {
    'Authorization': f'Bearer {openai.api_key}',
    'Content-Type': 'application/json',
    'OpenAI-Beta': 'assistants=v1'
}
data = {
    "file_id": file_id
}
# response = requests.post(url, headers=headers, data=json.dumps(data))
# print(response.json())
print("server booted")

@app.route('/stream', methods=['GET'])
def stream():
    def event_stream():
        while True:
            yield "data: Hello, world!\n\n"
            print("yo!")
            time.sleep(1)  # delay between messages
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print(f"Received request for {path}")
    return "URL not found", 404

@app.route('/stram')
def stram():
    def event_stream():
        while True:
            prompt = request.args.get('prompt')
            print(f"Received prompt {prompt}. Making first GPT call")
            if not prompt:
                return
            thread = client.beta.threads.create()
            # sse.publish({"message": f'Run {run.id} created, forming initial notes'}, type='response')
            refinement = False
            initial_notes = retrieval(prompt, thread.id, refinement)  # Replace with your function to generate responses
            sse.publish({"notes": initial_notes}, type='response')
            refinement = True
            refined_notes = retrieval(initial_notes, thread.id, refinement)
            sse.publish({"refined_notes": refined_notes}, type='response')
    return Response(event_stream(), mimetype="text/event-stream")
    
def retrieval(text, thread_id, refinement):
    try:
        print(f'running with prompt: {text}...')
        if refinement == False:
            instructions = f"Provide notes on {text}"
            ### Run research() async with {text}
        else:
            research = ["Dogs are yellow because they eat mustard", "Cats can fly because they have sharp clause"] ## Wait for research then run the next line
            instructions = f"Good start. Analyse these notes and adjust {research}"
        run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                model="gpt-4-1106-preview",
                instructions=instructions
            )
        # Periodically retrieve the Run to check status and see if it has completed
        while run.status != "completed":
            time.sleep(1.5)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
        sse.publish({"message": f'Run {run.id} completed'}, type='response')
        print('Run completed')

        all_messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        sse.publish({"message": all_messages.data[-1]}, type='response')
    
    except Exception as e:
        raise Exception(f'Error in generating content: {str(e)}')

def research(notes):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f'Suggest 1-3 topics for academic research relevant to the notes provided by the user. Return the topics as JSON [{"topic_1":"first topic"},{"topic_2":"second topic"}]:'},
            {"role": "user", "content": {notes}}
        ]
        )
    topics = response.choices[0].message.content
    # research = # tavily api with {topics}
    return research

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

if __name__ == '__main__':
    app.run(debug=True)


