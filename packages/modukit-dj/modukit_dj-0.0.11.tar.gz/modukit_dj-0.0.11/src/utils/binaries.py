import os
import platform
import re
import sys
import tarfile
import tempfile
from pathlib import Path

import requests
import typer


def resolve_modukit_binary():
    # Get environment variables via Typer
    github_pat = os.getenv("GITHUB_PAT")
    github_repo = os.getenv("GITHUB_REPO")

    if not github_repo:
        raise ValueError("Missing required environment variables (GITHUB_REPO, GITHUB_DOWNLOAD_URL).")

    # Detect OS and architecture
    system = platform.system().lower()
    arch = platform.machine().lower()
    if arch in ("x86_64", "amd64"):
        arch = "amd64"
    elif arch in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        typer.echo(f"Error: Unsupported architecture: {arch}", err=True)
        sys.exit(1)

    # Prepare temp directory
    temp_dir = Path(tempfile.gettempdir()) / "modukit/bin"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Prepare GitHub API request for latest release
    api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"
    headers = {"Authorization": f"token {github_pat}"}

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        release = response.json()
    except Exception as e:
        typer.echo(f"Error fetching release info: {e}", err=True)
        sys.exit(1)

    # After fetching the release object
    latest_version = release.get("tag_name", "").lstrip("v")

    # Find the highest version in the cache
    pattern = re.compile(r"modukit-(\d+\.\d+\.\d+)-.+-.+")
    cached_versions = []
    for folder in temp_dir.iterdir():
        if folder.is_dir():
            m = pattern.fullmatch(folder.name)
            if m:
                cached_versions.append((m.group(1), folder))

    if cached_versions:
        # Get the highest cached version
        cached_versions.sort(key=lambda x: tuple(map(int, x[0].split("."))), reverse=True)
        highest_cached_version, latest_folder = cached_versions[0]
        if highest_cached_version == latest_version:
            binary_name = "modukit.exe" if system == "windows" else "modukit"
            binary_path = latest_folder / binary_name
            if binary_path.exists() and os.access(binary_path, os.X_OK):
                return str(binary_path)

    # Find the correct asset
    asset_name = f"{system}-{arch}"
    asset = None
    for a in release.get("assets", []):
        if asset_name in a["name"]:
            asset = a
            break

    if not asset:
        typer.echo(f"Error: No binary found for {system}-{arch} in the latest release.", err=True)
        sys.exit(1)

    # Download the asset
    try:
        api_asset_url = asset["url"]
        download_headers = {
            "Authorization": f"token {github_pat}",
            "Accept": "application/octet-stream"
        }
        asset_response = requests.get(api_asset_url, headers=download_headers, stream=True, timeout=30)
        asset_response.raise_for_status()
    except Exception as e:
        typer.echo(f"Error downloading binary: {e}", err=True)
        sys.exit(1)

    # Save the binary
    binary_path = temp_dir / asset["name"]
    try:
        with open(binary_path, "wb") as f:
            for chunk in asset_response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        typer.echo(f"Error saving binary: {e}", err=True)
        sys.exit(1)

    typer.echo("New modukit binary downloaded")

    # Extract if .tar.gz
    if str(binary_path).endswith(".tar.gz"):
        try:
            with tarfile.open(binary_path, "r:gz") as tar:
                extractionPath = temp_dir / binary_path.name.split(".tar")[0]
                extractionPath.mkdir(parents=True, exist_ok=True)
                tar.extractall(path=extractionPath)
                binary_path = extractionPath / ("modukit.exe" if system == "windows" else "modukit")
            typer.echo(f"Extracted {binary_path} to {temp_dir}")
        except Exception as e:
            typer.echo(f"Error extracting binary: {e}", err=True)
            sys.exit(1)

    return str(binary_path)
