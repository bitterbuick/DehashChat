import openai
import requests
import json
import os
import sys

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEHASHED_API_KEY = os.getenv("DEHASHED_API_KEY")
SESSION_FILE = 'chat_sessions.json'

if not OPENAI_API_KEY:
    print("Missing OPENAI_API_KEY environment variable.")
    sys.exit(1)
if not DEHASHED_API_KEY:
    print("Missing DEHASHED_API_KEY environment variable.")
    sys.exit(1)

openai.api_key = OPENAI_API_KEY

# Initialize or load chat sessions
if os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, 'r') as file:
        chat_sessions = json.load(file)
else:
    chat_sessions = {}

def save_session(session_id, messages):
    chat_sessions[session_id] = messages
    with open(SESSION_FILE, 'w') as file:
        json.dump(chat_sessions, file)

def chatgpt_query(session_id, question):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=question,
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            user=session_id
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error querying ChatGPT: {e}")
        return None

def query_dehashed(parameters):
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {DEHASHED_API_KEY}',
    }
    try:
        response = requests.get('https://api.dehashed.com/search', headers=headers, params=parameters)
        return response.json()
    except Exception as e:
        print(f"Error querying Dehashed: {e}")
        return None

def main():
    session_id = 'user123'  # This could be dynamically generated or user-defined
    while True:
        question = input("Ask me anything: ")
        if question.lower() == 'exit':
            break
        
        chat_response = chatgpt_query(session_id, question)
        if chat_response:
            print(f"ChatGPT: {chat_response}")
            # Example: Convert chat_response to query parameters for Dehashed
            # This needs to be implemented based on the response and what information you're looking for
            dehashed_response = query_dehashed({'query': chat_response})  # Placeholder for actual implementation
            print(f"Dehashed Data: {dehashed_response}")
            
            # Save the session after each interaction
            if session_id not in chat_sessions:
                chat_sessions[session_id] = []
            chat_sessions[session_id].append({'question': question, 'chat_response': chat_response})
            save_session(session_id, chat_sessions[session_id])

if __name__ == "__main__":
    main()
