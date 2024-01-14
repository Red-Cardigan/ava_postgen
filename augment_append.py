# Create JSONL ver2 with augmentation
import os
import openai
from openai import OpenAI
import json
import psycopg2
from psycopg2 import sql
import random
import nlpaug.augmenter.word as naw

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="cardigan"
)
cur = conn.cursor()

system_prompt ="You are an AI trained on a diverse set of blog posts. Your task is to generate content using the provided notes. Be insightful and adapt your tone to the topic presented, ranging from formal to casual as needed."

def generate_sentences(post, num_sentences=3):
    user_content = []
    gpt_used = False
    gpt = None
    if post[4] is not None:
        gpt = post[4]
    elif post[5] is not None:
        gpt = post[5]       

    if gpt is not None:
        if '\n' in gpt:
            gpt = gpt.split('\n', 1)[1]
        elif ':' in gpt:
            gpt = gpt.split(':', 1)[1]
        elif 'style' in gpt:
            gpt = gpt.split('style', 1)[1]

    while len(user_content) < num_sentences:
        parts_included = 0
        while parts_included < 2:
            parts = [
                ("called '" + post[0] + "'", random.choice([True, False])),  # Title
                ("with description '" + post[1] + "'", random.choice([True, False])),  # Description
                ("using tags '" + post[2] + "'", random.choice([True, False]))  # Tags
            ]
            parts_included = sum([include for _, include in parts])

        if post[6] >= 150:
            adjectives = ['n excellent', ' fantastic', ' very good', ' high quality', ' successful']
            adjective = random.choice(adjectives)
            prepend = f"Write a{adjective} blog post "
        elif post[6] >= 35:
            adjectives = [' good', ' decent', ' satisfactory', ' reasonably good']
            adjective = random.choice(adjectives)
            prepend = f"Write a{adjective} blog post "
        else:
            prepend = "Write a blog post "
        sentence = prepend
        for part, include in parts:
            if include:
                sentence += part + " "

        # If style notes are not included, add default style
        if gpt and (not gpt_used or random.choice([True, False])):
            sentence += ". \nStyle notes: " + gpt
            gpt_used = True
        else:
            sentence += "in your personal style"

        user_content.append(sentence + "\n\n")

    # Add a sentence with all parts included
    sentence = prepend + "'" + post[0] + "' with description '" + post[1] + "' using tags " + post[2]
    if gpt:
        sentence += ". \nStyle notes:\n" + gpt
    else:
        sentence += "in your personal style."
    user_content.append(sentence + "\n\n")

    return list(user_content)

def create_interaction(sentence, post, aug_p, interactions, augment=True):
    # Create the augmenter
    aug = naw.RandomWordAug(aug_p=aug_p, aug_max=None)

    # Augment the text if required
    if augment:
        content = aug.augment(post[3])
    else:
        content = post[3]

    # Create the interaction
    interaction = {"messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": sentence},
        {"role": "assistant", "content": content}
    ]}
    interactions.append(interaction)
    

# Check if the file exists
file_exists = os.path.isfile('ava_training_ver2.jsonl')

batch_size = 50

# Query to fetch the posts
query = "SELECT item_title, item_description, gpt_tags_str, item_content, gpt4, gpt3, reactions, id FROM top_writer_posts LIMIT %s OFFSET %s"

# Query to get the count of rows
count_query = "SELECT COUNT(*) FROM top_writer_posts"
cur.execute(count_query)
count = cur.fetchone()[0]
print(f"Number of rows returned: {count}")

# Fetch rows in batches
offset = 0
while offset < count:
    # print(cur.mogrify(query, (batch_size, offset)))
    cur.execute(query, (batch_size, offset))
    posts = cur.fetchall()
    if not posts:
        break

# Open the file in append mode if it exists, otherwise create a new file
    with open('ava_training_ver2.jsonl', 'a' if file_exists else 'w') as f:
                # System prompt
        for post in posts:
            interactions = []
            user_content = generate_sentences(post)
            for sentence in user_content:
                if post[6] >= 150:
                    create_interaction(sentence, post, 0.05, interactions, augment=False)  # No augmentation for the first interaction
                    create_interaction(sentence, post, 0.05, interactions)  # First augmented interaction
                    create_interaction(sentence, post, 0.05, interactions)  # Second augmented interaction
                elif post[6] >= 35:
                    create_interaction(sentence, post, 0.1, interactions, augment=False)  # No augmentation for the first interaction
                    create_interaction(sentence, post, 0.1, interactions)  # First augmented interaction
                    create_interaction(sentence, post, 0.1, interactions)  # Second augmented interaction
                else: 
                    create_interaction(sentence, post, 0.2, interactions, augment=False)  # No augmentation for the first interaction
                    create_interaction(sentence, post, 0.2, interactions)  # First augmented interaction
                    create_interaction(sentence, post, 0.2, interactions)  # Second augmented interaction
            
            # Write to the JSONL file
            if interactions:
                f.write('\n'.join(json.dumps(interaction) for interaction in interactions) + '\n')

            update_query = "UPDATE top_writer_posts SET appended_to_jsonl = TRUE WHERE id = %s"
            cur.execute(update_query, (post[7],))
            conn.commit()
    
    offset += batch_size

cur.close()
conn.close()