# agno-poc

Proof of concept built with the AGNO framework (www.agno.com) for an AI agent experience, covering chat, YouTube summarization, team collaboration, and tracing/observability.

## Overview
This POC uses AGNO (www.agno.com) and demonstrates how to:
- Orchestrate agent interactions and tools
- Run a chat-style UI
- Summarize or analyze YouTube content
- Collaborate in a team/agent swarm
- Capture traces for debugging and performance

## Features
- Chat interface
- YouTube agent
- Team collaboration
- Tracing/observability

## Prerequisites
- Node.js (LTS recommended)
- Python 3.10+ (if the backend uses Python)
- API keys for any LLMs or external services used

## Setup
1. Clone the repository.
2. Install dependencies for each package/module.
3. Create a `.env` file based on `.env.example` (if present).
4. Add required API keys and configuration.

## Configuration
## Set this env variable
- `OPENAI_API_KEY`


Adjust these to match your runtime and provider.

## Run
1. `docker compose up -d --build`
2. Open the AGNO control plane at www.os.agno.com and point it to `http://localhost:8000`.


## Usage
- Chat: open the chat UI and send a prompt.
- YouTube agent: provide a YouTube URL to summarize or analyze.
- Team: trigger multi-agent workflows (if exposed in UI).
- Tracing: inspect logs/traces in the configured dashboard.

## Project Structure
- `/agentos-railway/agent` and `/agentos-railway/team`-> Defined agents and teams.

## Screenshots

## Chat
<img width="1600" height="935" alt="image" src="https://github.com/user-attachments/assets/aeba4377-3a23-4a00-9128-104f5fcebc38" />

## Youtube agent
<img width="1706" height="908" alt="image" src="https://github.com/user-attachments/assets/34c36b6f-487b-4263-a96e-d91c7581a653" />


## Team
<img width="1600" height="851" alt="image" src="https://github.com/user-attachments/assets/dab153f0-ce20-4acc-bea7-c56395683026" />



## Tracing
<img width="1600" height="911" alt="image" src="https://github.com/user-attachments/assets/dd6913e9-8e8b-42bc-bab6-b2de73eb3029" />
