import openai
import requests
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
DEHASHED_API_KEY = os.getenv("DEHASHED_API_KEY", "").strip()
SESSION_FILE = 'chat_sessions.json'

# Validation
if not OPENAI_API_KEY:
    print("Error: Missing OPENAI_API_KEY environment variable.")
    sys.exit(1)
if not DEHASHED_API_KEY:
    print("Error: Missing DEHASHED_API_KEY environment variable.")
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

def query_dehashed_password(password):
    """
    Search for a password using the FREE DeHashed password search endpoint.
    This endpoint hashes the password with SHA-256 and checks if it exists.
    """
    import hashlib
    
    url = "https://api.dehashed.com/v2/search-password"
    
    # Hash the password with SHA-256
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'DeHashed-Api-Key': DEHASHED_API_KEY,
    }
    
    body = {
        'sha256_hashed_password': sha256_hash
    }

    print(f"\n[DEBUG] Querying DeHashed PASSWORD search (FREE) with hash: {sha256_hash[:16]}...")
    
    try:
        response = requests.post(url, json=body, headers=headers)
        
        print(f"[DEBUG] Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results_found = data.get('results_found', 0)
            return json.dumps({
                "found": results_found > 0,
                "count": results_found,
                "message": f"Password found in {results_found} breaches" if results_found > 0 else "Password not found in any known breaches"
            })
        else:
            return json.dumps({"error": f"API Request failed with status code {response.status_code}", "body": response.text})

    except Exception as e:
        return json.dumps({"error": str(e)})

def query_dehashed_search(query):
    """
    Execute a general search against the DeHashed API (requires credits).
    """
    url = "https://api.dehashed.com/v2/search"
    
    headers = {
        'Content-Type': 'application/json',
        'DeHashed-Api-Key': DEHASHED_API_KEY,
    }
    
    body = {
        'query': query,
        'page': 1,
        'size': 100,
        'de_dupe': True
    }

    print(f"\n[DEBUG] Querying DeHashed SEARCH (requires credits) with: {query} ...")
    
    try:
        response = requests.post(url, json=body, headers=headers)
        
        print(f"[DEBUG] Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'entries' in data and data['entries']:
                simplified_entries = []
                for entry in data['entries'][:10]:
                    simplified_entries.append({
                        'email': entry.get('email'),
                        'username': entry.get('username'),
                        'password': entry.get('password'),
                        'hashed_password': entry.get('hashed_password'),
                        'database': entry.get('database_name'),
                        'ip_address': entry.get('ip_address'),
                        'phone': entry.get('phone')
                    })
                return json.dumps({
                    "count": data.get('total', 0),
                    "balance": data.get('balance', 0),
                    "results": simplified_entries
                })
            else:
                return json.dumps({"message": "No results found.", "balance": data.get('balance', 0)})
        elif response.status_code == 401:
            # User doesn't have search access - suggest password search instead
            return json.dumps({
                "error": "Search API requires an active subscription. Use password search instead (it's free!).",
                "suggestion": "Try asking: 'Is password XYZ compromised?'"
            })
        else:
            return json.dumps({"error": f"API Request failed with status code {response.status_code}", "body": response.text})

    except Exception as e:
        return json.dumps({"error": str(e)})

def run_conversation(session_id):
    # Retrieve history or start new
    messages = chat_sessions.get(session_id, [])
    
    # Validate message format compatibility
    if messages and ('role' not in messages[0]):
        print("[INFO] Old session format detected. Starting new session.")
        messages = []

    if not messages:
        messages = [
            {"role": "system", "content": """You are a DeHashed security analyst assistant. You have access to DeHashed API functions.

**search_dehashed**: Search for passwords, emails, usernames, IPs, etc. in the DeHashed database.
- For PASSWORD searches: "password:actual_password_text"
- For EMAIL searches: "email:user@example.com"  
- For USERNAME searches: "username:john"

**CRITICAL RESPONSE GUIDELINES**:

1. **Initial Response - Be Concise**:
   - Provide a SHORT summary (2-3 sentences max)
   - State: Total count found, key databases (top 2-3 only)
   - Example: "Found in 29 breaches across databases like ALIEN TXTBASE, Collections, and Exploit.in. The password appears with several email addresses."
   
2. **Invite Follow-up**:
   - Always end with: "Would you like to see specific details like affected emails, databases, or hashed password formats?"
   - OR: "I can show you more details if needed - just ask!"
   
3. **Answering Follow-up Questions**:
   - User asks "what emails?": List the unique emails
   - User asks "which databases?": List all database names
   - User asks "show details": Provide more comprehensive info
   - Always reference the PREVIOUS search results in context
   
4. **Never Dump Raw JSON**: Always interpret data into natural language

5. **No Results**: If count is 0, be direct: "No matches found in the DeHashed database."

Remember: The full JSON data is in your conversation history. Users can ask follow-up questions about ANY previous search result."""}
        ]

    print("**************************************************")
    print("*               Welcome to DehashChat            *")
    print("*                                                *")
    print("* Interact with ChatGPT and pivot to DeHashed    *")
    print("* API for data enrichment.                       *")
    print("*                                                *")
    print("* Type 'exit' to quit the application.           *")
    print("**************************************************")
    print()

    while True:
        try:
            user_input = input("Ask me anything: ")
            if user_input.strip().lower() == 'exit':
                break

            messages.append({"role": "user", "content": user_input})

            # Define the function for OpenAI - only one function now
            functions = [
                {
                    "name": "search_dehashed",
                    "description": "Search DeHashed database for passwords, emails, usernames, IPs, phone numbers, etc. Use field:value syntax like 'password:mypassword' or 'email:test@example.com'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query using DeHashed syntax. For passwords use 'password:actual_text', for emails use 'email:user@domain.com', etc."
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
                
                # Call the general search function
                if function_name == "search_dehashed":
                    function_response = query_dehashed_search(
                        query=function_args.get("query"),
                    )
                else:
                    function_response = json.dumps({"error": f"Unknown function: {function_name}"})

                # Print the raw result for the user to see immediately
                try:
                    parsed_debug = json.loads(function_response)
                    print(f"\n[DEBUG] DeHashed Raw Response: {json.dumps(parsed_debug, indent=2)}\n")
                except:
                    print(f"\n[DEBUG] DeHashed Raw Response: {function_response}\n")

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
