import openai
import requests
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEHASHED_API_KEY = os.getenv("DEHASHED_API_KEY")
DEHASHED_EMAIL = os.getenv("EMAIL_ADDRESS") # Using EMAIL_ADDRESS to match .env.example
SESSION_FILE = 'chat_sessions.json'

# Validation
if not OPENAI_API_KEY:
    print("Error: Missing OPENAI_API_KEY environment variable.")
    sys.exit(1)
if not DEHASHED_API_KEY:
    print("Error: Missing DEHASHED_API_KEY environment variable.")
    sys.exit(1)
if not DEHASHED_EMAIL:
    print("\n[ERROR] Missing EMAIL_ADDRESS environment variable.")
    print("Please update your .env file to include:")
    print("EMAIL_ADDRESS=your_email@example.com")
    print("This is required for DeHashed authentication.\n")
    sys.exit(1)

openai.api_key = OPENAI_API_KEY

# Initialize or load chat sessions
if os.path.exists(SESSION_FILE):
    try:
        with open(SESSION_FILE, 'r') as file:
            chat_sessions = json.load(file)
    except json.JSONDecodeError:
        chat_sessions = {}
else:
    chat_sessions = {}

def save_session(session_id, messages):
    # Only save the last 20 messages to keep file size manageable
    chat_sessions[session_id] = messages[-20:] 
    with open(SESSION_FILE, 'w') as file:
        json.dump(chat_sessions, file)

def query_dehashed(query):
    """
    Execute a search against the DeHashed API.
    """
    url = "https://api.dehashed.com/search"
    headers = {
        'Accept': 'application/json',
    }
    # DeHashed uses Basic Auth: (email, api_key)
    # The 'query' parameter is passed in the URL parameters
    params = {
        'query': query,
        'size': 100 # Default limit
    }
    
    print(f"\n[DEBUG] Querying DeHashed with: {query} ...")
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            auth=(DEHASHED_EMAIL, DEHASHED_API_KEY)
        )
        
        if response.status_code == 200:
            data = response.json()
            # If successful, return the entries or a summary
            # We explicitly check strictly for 'entries'
            if 'entries' in data and data['entries']:
                 # Simplify the data to save tokens
                simplified_entries = []
                for entry in data['entries'][:10]: # Limit to top 10 for context window
                    simplified_entries.append({
                        'email': entry.get('email'),
                        'username': entry.get('username'),
                        'password': entry.get('password'),
                        'hashed_password': entry.get('hashed_password'),
                        'database': entry.get('database_name'),
                        'source': entry.get('source')
                    })
                return json.dumps({"count": data.get('total', 0), "results": simplified_entries})
            else:
                return json.dumps({"message": "No results found.", "details": data})
        else:
            return json.dumps({"error": f"API Request failed with status code {response.status_code}", "body": response.text})

    except Exception as e:
        return json.dumps({"error": str(e)})

def run_conversation(session_id):
    # Retrieve history or start new
    messages = chat_sessions.get(session_id, [
        {"role": "system", "content": "You are a helpful security assistant. You have access to the DeHashed API to check for compromised data. When a user asks to check if something was leaked (email, IP, username, etc.), use the 'search_dehashed' function. Construct a precise DeHashed query (e.g., 'email:test@example.com' or 'ip:1.2.3.4'). Always interpret the JSON results from DeHashed and provide a natural language summary to the user. Do not simply dump the JSON. If the result contains passwords, warn the user strictly."}
    ])

    print("**************************************************")
    print("*               Welcome to DehashChat            *")
    print("*                                                *")
    print("* Interact with ChatGPT and pivot to DeHashed    *")
    print("* API for data enrichment.                       *")
    print("*                                                *")
    print("* Type 'exit' to quit the application.           *")
    print("**************************************************\n")

    while True:
        try:
            user_input = input("Ask me anything: ")
            if user_input.lower() in ['exit', 'quit']:
                break

            messages.append({"role": "user", "content": user_input})

            # Define the function for OpenAI
            functions = [
                {
                    "name": "search_dehashed",
                    "description": "Search the DeHashed database for leaks/breaches",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query, e.g. 'email:jdoe@example.com' or 'username:admin'. Use specific field qualifiers if possible."
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]

            # First call to OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                functions=functions,
                function_call="auto", 
            )

            response_message = response["choices"][0]["message"]

            # Check if the model wants to call a function
            if response_message.get("function_call"):
                # Call the function
                function_name = response_message["function_call"]["name"]
                function_args = json.loads(response_message["function_call"]["arguments"])
                
                if function_name == "search_dehashed":
                    function_response = query_dehashed(
                        query=function_args.get("query"),
                    )

                    # Append the assistant's function call message
                    messages.append(response_message)
                    
                    # Append the function result
                    messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    })

                    # Second call to OpenAI to get the natural response
                    second_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                    )
                    
                    answer = second_response["choices"][0]["message"]["content"]
                    print(f"\nChatGPT: {answer}\n")
                    messages.append({"role": "assistant", "content": answer})

            else:
                # No function call, just a normal reply
                answer = response_message["content"]
                print(f"ChatGPT: {answer}\n")
                messages.append({"role": "assistant", "content": answer})

            # Save session
            save_session(session_id, messages)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    session_id = 'user123' 
    run_conversation(session_id)
