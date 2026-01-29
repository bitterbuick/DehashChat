# DehashChat

Python CLI using ChatGPT and DeHashed API for natural language queries.

## Quick Start (Docker Compose) - Recommended

The easiest way to run the application is using Docker Compose.

### Prerequisites

1.  **Docker & Docker Compose**: Ensure Docker Desktop is installed.
2.  **API Keys**: You need an OpenAI API Key and a DeHashed API Key.

### Setup

1.  Clone this repository.
2.  Copy the example environment file:
    ```sh
    cp .env.example .env
    ```
3.  Edit `.env` and add your API keys:
    ```
    OPENAI_API_KEY=your_actual_key
    DEHASHED_API_KEY=your_actual_key
    EMAIL_ADDRESS=your_email_address
    ```

### Run

### Run

1.  **Configure Environment**:
    Ensure your `.env` file contains the `EMAIL_ADDRESS` field (required for DeHashed):
    ```
    EMAIL_ADDRESS=your_email@example.com
    ```

2.  **Start the App**:
    ```sh
    docker-compose run --rm dehashchat
    ```

This will build the image (if needed), start the container, and drop you into the interactive prompt.

---

## Troubleshooting DeHashed API

If you encounter `401 Unauthorized` or `404 Not Found` errors:

### Verify API Credentials

1.  **Check your DeHashed account**: Log in to [DeHashed](https://www.dehashed.com/) and verify:
    -   You have an active subscription with API access
    -   Your API key is correctly copied from your account dashboard
    -   Your `EMAIL_ADDRESS` matches your DeHashed login email exactly

2.  **Test API manually** with `curl`:
    ```bash
    curl -u "your_email@example.com:your_api_key" \
         "https://api.dehashed.com/search?query=email:test@example.com"
    ```

3.  **Common Issues**:
    -   **Wrong endpoint**: DeHashed has changed endpoints. Try `/search` vs `/v2/search`
    - **Whitespace**: Ensure no extra spaces/newlines in your `.env` file values
    -   **Account tier**: Free accounts may not have API access 
    -   **Quota exceeded**: Check if you've hit your API rate limit

If the `curl` command also fails with 401/404, there's an issue with your DeHashed credentials or account, not this application.

---

## Local Development (No Docker)

If you prefer running Docker manually:

1.  **Build**:
    ```sh
    docker build -t dehashchat .
    ```

2.  **Run**:
    ```sh
    docker run -it --env-file .env dehashchat
    ```

## Local Development (No Docker)

1.  Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
2.  Ensure `.env` is configured.
3.  Run the script:
    ```sh
    python Chat.py
    ```
