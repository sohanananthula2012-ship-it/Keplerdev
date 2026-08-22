#!/usr/bin/env python3
"""
GitHub Repository Uploader Script (With Rate-Limit Backoff)
Uploads workspace files to a GitHub repository using the GitHub Git Data API.

Usage:
  GITHUB_TOKEN="your_pat_here" python3 scripts/push_to_github.py --repo "owner/repo_name" --branch "main"
"""

import os
import sys
import json
import time
import base64
import argparse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

# Files/folders to exclude from upload
EXCLUDE_DIRS = {'.git', 'node_modules', 'dist', '.next', '.enter'}
EXCLUDE_FILES = {'pnpm-lock.yaml', '.DS_Store'}

def github_api_request(url, token, data=None, method='GET', retries=5):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Enter-GitHub-Uploader',
        'Content-Type': 'application/json'
    }
    req_data = json.dumps(data).encode('utf-8') if data else None

    for attempt in range(retries):
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                if response.status in (200, 201):
                    return json.loads(response.read().decode('utf-8'))
                return None
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"Rate limited (status {e.code}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                error_body = e.read().decode('utf-8')
                print(f"API Error ({e.code}) on {url}: {error_body}")
                sys.exit(1)

def get_workspace_files(workspace_root):
    file_paths = []
    for root, dirs, files in os.walk(workspace_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f in EXCLUDE_FILES:
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, workspace_root)
            file_paths.append((full_path, rel_path))
    return file_paths

def upload_single_blob(base_url, token, full_path, rel_path):
    with open(full_path, 'rb') as fp:
        content = fp.read()
    
    encoded_content = base64.b64encode(content).decode('utf-8')
    blob_res = github_api_request(
        f'{base_url}/git/blobs',
        token,
        data={'content': encoded_content, 'encoding': 'base64'},
        method='POST'
    )
    blob_sha = blob_res['sha']
    time.sleep(0.05)  # Avoid secondary rate limits
    return {
        'path': rel_path.replace('\\', '/'),
        'mode': '100644',
        'type': 'blob',
        'sha': blob_sha
    }

def push_to_github(repo, token, branch='main', commit_message='Full export: source, skills, prompts, config, assets'):
    base_url = f'https://api.github.com/repos/{repo}'
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    print(f"Scanning workspace files from {workspace_root}...")
    files = get_workspace_files(workspace_root)
    print(f"Found {len(files)} files to upload.")

    # 1. Get reference to current branch head
    ref_info = github_api_request(f'{base_url}/git/ref/heads/{branch}', token)
    latest_commit_sha = ref_info['object']['sha']
    print(f"Current head commit for {branch}: {latest_commit_sha}")

    # 2. Get base tree SHA from latest commit
    commit_info = github_api_request(f'{base_url}/git/commits/{latest_commit_sha}', token)
    base_tree_sha = commit_info['tree']['sha']

    # 3. Create blobs for all files in parallel with rate limit safety
    print("Uploading file blobs...")
    tree_items = []
    completed_count = 0
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(upload_single_blob, base_url, token, full_path, rel_path): rel_path
            for full_path, rel_path in files
        }
        for future in as_completed(futures):
            item = future.result()
            tree_items.append(item)
            completed_count += 1
            if completed_count % 50 == 0 or completed_count == len(files):
                print(f"  Progress: {completed_count}/{len(files)} files uploaded...")

    # 4. Create new tree
    print("Creating new Git tree...")
    tree_res = github_api_request(
        f'{base_url}/git/trees',
        token,
        data={'base_tree': base_tree_sha, 'tree': tree_items},
        method='POST'
    )
    new_tree_sha = tree_res['sha']

    # 5. Create commit
    print("Creating commit...")
    commit_res = github_api_request(
        f'{base_url}/git/commits',
        token,
        data={
            'message': commit_message,
            'tree': new_tree_sha,
            'parents': [latest_commit_sha]
        },
        method='POST'
    )
    new_commit_sha = commit_res['sha']

    # 6. Update branch ref
    print(f"Updating branch {branch} to {new_commit_sha}...")
    github_api_request(
        f'{base_url}/git/refs/heads/{branch}',
        token,
        data={'sha': new_commit_sha, 'force': True},
        method='PATCH'
    )

    print(f"\nSUCCESS! Pushed {len(files)} files.")
    print(f"Commit Hash: {new_commit_sha}")
    print(f"Repository URL: https://github.com/{repo}")
    print(f"Branch: {branch}")

def main():
    parser = argparse.ArgumentParser(description="Push project workspace to GitHub API")
    parser.add_argument("--repo", required=True, help="GitHub repository in 'owner/repo' format (e.g. 'octocat/Hello-World')")
    parser.add_argument("--branch", default="main", help="Target branch (default: 'main')")
    parser.add_argument("--message", default="Full export: source, skills, prompts, config, assets", help="Commit message")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is missing.")
        sys.exit(1)

    push_to_github(args.repo, token, branch=args.branch, commit_message=args.message)

if __name__ == "__main__":
    main()
