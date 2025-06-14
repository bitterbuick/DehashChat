# DehashChat
Python CLI using ChatGPT and DeHashed API for natural language queries

# Running the Python CLI App in Docker

This guide outlines how to run the Python CLI application, which interacts with ChatGPT and DeHashed APIs, inside a Docker container.

## Prerequisites

- Docker installed on your system. If you haven't installed Docker yet, follow the [official Docker installation guide](https://docs.docker.com/get-docker/).
- An API key for OpenAI (ChatGPT) and an API key for DeHashed. You'll need these to interact with the respective services.

## Step 1: Prepare Your Application

Ensure your Python application (`Chat.py`) and the `requirements.txt` file listing all necessary Python packages are in the same directory. Your `requirements.txt` should include:

```
openai
requests
```

## Step 2: Create a Dockerfile

Create a file named `Dockerfile` in the same directory as your Python application with the following content:

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run Chat.py when the container launches
CMD ["python", "./Chat.py"]
```

## Step 3: Build the Docker Image

Open a terminal or command prompt. Navigate to the directory containing your Dockerfile and run the following command, replacing `<your-image-name>` with a name for your Docker image:

```sh
docker build -t <your-image-name> .
```

This command builds a new Docker image based on the instructions in your Dockerfile.

## Step 4: Run Your Docker Container

After building the image, start your container with:

```sh
docker run -it <your-image-name>
```

The `-it` flags attach your terminal to the container, allowing you to interact with the CLI app directly.

## Providing API Keys via Environment Variables

To avoid hardcoding your API keys in the application, provide them when you start the container. Pass them directly with `docker run -e`:

```sh
docker run -it \
  -e OPENAI_API_KEY="your_openai_api_key_here" \
  -e DEHASHED_API_KEY="your_dehashed_api_key_here" \
  <your-image-name>
```

You can also place the variables in a `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
DEHASHED_API_KEY=your_dehashed_api_key_here
```

and load them with the `--env-file` option:

```sh
docker run -it --env-file .env <your-image-name>
```

Replace `your_openai_api_key_here` and `your_dehashed_api_key_here` with your actual API keys.

## Note on Persistent Storage

If your application saves data and you wish this data to persist across container runs, consider using Docker volumes. Consult the Docker documentation on volumes for more information.


Make sure to replace placeholder texts like `<your-image-name>`, `your_openai_api_key_here`, and `your_dehashed_api_key_here` with actual values where applicable. This markdown guide provides a comprehensive overview for users on running your Python CLI application within a Docker environment, covering everything from setup to execution.
