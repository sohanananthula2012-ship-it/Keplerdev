#!/usr/bin/env python3
"""Push a local file to the Keplerdev GitHub repo via the Contents API."""
import base64, json, os, sys, urllib.request

REPO = os.environ["GITHUB_REPO"]
BRANCH = os.environ.get("GITHUB_BRANCH", "main")
TOKEN = os.environ["GITHUB_TOKEN"]

def push(local_path, repo_path, msg):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    url = f"https://api.github.com/repos/{REPO}/contents/{repo_path}"
    # get sha if exists
    sha = None
    req = urllib.request.Request(url + f"?ref={BRANCH}",
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req) as r:
            sha = json.load(r).get("sha")
    except Exception:
        pass
    data = {"message": msg, "content": content, "branch": BRANCH}
    if sha:
        data["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"},
        method="PUT")
    with urllib.request.urlopen(req) as r:
        resp = json.load(r)
    print("pushed", repo_path, "->", resp["content"]["html_url"])

if __name__ == "__main__":
    local, repo_path = sys.argv[1], sys.argv[2]
    msg = sys.argv[3] if len(sys.argv) > 3 else f"update {repo_path}"
    push(local, repo_path, msg)
