# src/pbot/commands/init/github_init.py
import os
import base64
import requests
import typer

GITHUB_API = "https://api.github.com"
TOKEN = "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"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def create_repo(name: str, description: str, private=True):
    data = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": True
    }

    response = requests.post(f"{GITHUB_API}/user/repos", headers=HEADERS, json=data)

    if response.status_code == 201:
        return response.json()  # success
    else:
        typer.secho(f"❌ Failed to create repo: {response.status_code}", fg=typer.colors.RED)
        typer.echo(response.json())
        raise typer.Exit(1)

def upload_file(owner, repo, path, content, commit_msg="Add file"):
    content_encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"

    # First: Check if file exists to get its SHA
    get_resp = requests.get(url, headers=HEADERS)

    data = {
        "message": commit_msg,
        "content": content_encoded,
    }

    if get_resp.status_code == 200:
        existing_file = get_resp.json()
        data["sha"] = existing_file["sha"]  # required for updating existing files

    put_resp = requests.put(url, headers=HEADERS, json=data)

    if put_resp.status_code in [200, 201]:
        typer.secho(f"✅ Uploaded: {path}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"❌ Failed to upload {path}", fg=typer.colors.RED)
        typer.echo(put_resp.json())
        raise typer.Exit(1)
