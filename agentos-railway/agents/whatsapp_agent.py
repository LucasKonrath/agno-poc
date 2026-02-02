import base64
import json
import re
from datetime import datetime
from os import getenv
from typing import Dict, Optional, Tuple

import requests
from openai import OpenAI

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIResponses
from agno.os import AgentOS
from agno.os.interfaces.whatsapp import Whatsapp
from agno.tools.decorator import tool


def _github_api_base() -> str:
    return getenv("GITHUB_API_BASE", "https://api.github.com").rstrip("/")


def _github_headers() -> Dict[str, str]:
    token = getenv("GITHUB_ACCESS_TOKEN") or getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_ACCESS_TOKEN is not set")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or f"whatsapp-app-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"


def _create_repo_and_upload_files(
    name: str,
    files: Dict[str, str],
    description: Optional[str],
    private: bool,
    organization: Optional[str],
    default_branch: str,
) -> str:
    api_base = _github_api_base()
    headers = _github_headers()
    payload = {
        "name": name,
        "description": description or "",
        "private": private,
        "auto_init": False,
    }

    if organization:
        create_url = f"{api_base}/orgs/{organization}/repos"
    else:
        create_url = f"{api_base}/user/repos"

    create_resp = requests.post(create_url, headers=headers, json=payload, timeout=30)
    if create_resp.status_code not in (201, 202):
        raise ValueError(f"Failed to create repo: {create_resp.status_code} {create_resp.text}")

    repo = create_resp.json()
    owner = repo["owner"]["login"]
    repo_name = repo["name"]

    for path, content in files.items():
        if not path or path.startswith("/") or ".." in path.split("/"):
            raise ValueError(f"Invalid file path: {path}")
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        file_url = f"{api_base}/repos/{owner}/{repo_name}/contents/{path}"
        file_payload = {
            "message": f"Add {path}",
            "content": encoded,
            "branch": default_branch,
        }
        file_resp = requests.put(file_url, headers=headers, json=file_payload, timeout=30)
        if file_resp.status_code not in (200, 201):
            raise ValueError(f"Failed to create file {path}: {file_resp.status_code} {file_resp.text}")

    result = {
        "full_name": repo.get("full_name"),
        "url": repo.get("html_url"),
        "private": repo.get("private"),
    }
    return json.dumps(result, indent=2)


def _generate_files_from_spec(spec: str, name: str) -> Tuple[Dict[str, str], Optional[str]]:
    client = OpenAI(api_key=getenv("OPENAI_API_KEY"))
    model = getenv("OPENAI_CODE_MODEL", "gpt-5.2")

    system_prompt = (
        "You are a senior software engineer. Generate a minimal, working project based on the spec. "
        "Return ONLY a JSON object with keys: files (object path->content), description (string). "
        "Always include README.md with run instructions. No markdown, no extra text."
    )
    user_prompt = f"Repo name: {name}\nSpec: {spec}\n"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    files = data.get("files") or {}
    description = data.get("description")

    if not isinstance(files, dict) or not files:
        raise ValueError("Generated files are empty or invalid")

    return files, description


@tool(
    name="generate_code_and_create_repo",
    description="Generate project code from a spec and create a GitHub repo with those files.",
    strict=True,
    instructions=(
        "Always call this tool with a JSON object of arguments. "
        "Required: spec (string). Optional: name (string), description (string), private (boolean), "
        "organization (string), default_branch (string). "
        "If name is omitted, a slug will be generated."
    ),
)
def generate_code_and_create_repo(
    spec: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    private: bool = True,
    organization: Optional[str] = None,
    default_branch: str = "main",
) -> str:
    """Generate code from a spec and create a GitHub repository.

    Args:
        spec: Description of the project to generate.
        name: Repository name (optional; slugified if omitted).
        description: Optional repository description.
        private: Whether the repository is private.
        organization: Optional GitHub org name. If omitted, uses the authenticated user.
        default_branch: Branch to create files on (default: main).

    Returns:
        JSON string with repository details.
    """
    if not name:
        name = _slugify(spec)
    if "/" in name:
        raise ValueError("Invalid repository name")

    if not organization:
        organization = getenv("GITHUB_ORG") or None
    files, generated_description = _generate_files_from_spec(spec=spec, name=name)
    final_description = description or generated_description or spec[:160]

    return _create_repo_and_upload_files(
        name=name,
        files=files,
        description=final_description,
        private=private,
        organization=organization,
        default_branch=default_branch,
    )

agent_db = SqliteDb(db_file="tmp/persistent_memory.db")
instructions = """
You are a WhatsApp coding agent. When a user asks for code, you:
1) don't ask anything back
2) Generate a minimal, working project with a README.
3) Create a new GitHub repo and upload the files using the tool.

Rules:
- Never reveal or request access tokens.
- Use sensible defaults if the user doesn’t specify (Python, Node, or simple HTML depending on request).
- Always include a README.md that explains how to run the code.
- Always call the tool with valid JSON arguments. Do NOT output non-JSON tool arguments.
- Pass the full user request as the tool's spec.
- After the tool call, reply to the user with the repo URL from the tool result.
"""

basic_agent = Agent(
    name="Basic Agent",
    model=OpenAIResponses(id="gpt-5.2", store=False),
    db=agent_db,
    instructions=instructions,
    tools=[generate_code_and_create_repo],
    tool_choice={"type": "function", "name": "generate_code_and_create_repo"},
    tool_call_limit=2,
    add_history_to_context=True,
    num_history_runs=3,
    add_datetime_to_context=True,
    markdown=True,
)

agent_os = AgentOS(
    agents=[basic_agent],
    interfaces=[Whatsapp(agent=basic_agent)],
)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="basic:app", reload=True)