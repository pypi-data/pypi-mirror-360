from datetime import datetime
import requests
import webbrowser
import socket
from .config import (
    API_BASE_URL,
    EXT_TO_LANG,
    SUCCESS_STYLE,
    WARNING_STYLE,
    ERROR_STYLE,
    INFO_STYLE,
    COOKIE_FILE,
)
import typer
from rich.console import Console
import re
import os
import zipfile
import subprocess


def save_cookie(cookie: str):
    """Save authentication cookie to file for persistent login."""
    with open(COOKIE_FILE, "w") as f:
        f.write(cookie)


def load_cookie() -> str:
    """Load authentication cookie from file."""
    if COOKIE_FILE.exists():
        with open(COOKIE_FILE, "r") as f:
            cookie = f.read().strip()
            return cookie
    return ""


def format_date(date_str):
    """Format date string to YYYY-MM-DD."""
    if not date_str or date_str == "N/A":
        return ""
    try:
        return datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
    except Exception:
        return date_str


def get_open_port():
    """Get an open port on the machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def open_browser(url):
    """Open a URL in the default browser."""
    try:
        webbrowser.open(url)
        return None
    except Exception as e:
        return e


def print_success(message: str):
    """Print a success message using the configured style."""
    console = Console()
    console.print(f"[{SUCCESS_STYLE}]{message}[/{SUCCESS_STYLE}]")


def print_warning(message: str):
    """Print a warning message with 'Warning:' prefix using the configured style."""
    console = Console()
    console.print(f"[{WARNING_STYLE}]Warning: {message}[/{WARNING_STYLE}]")


def print_error(message: str):
    """Print an error message with 'Error:' prefix using the configured style."""
    console = Console()
    console.print(f"[{ERROR_STYLE}]Error: {message}[/{ERROR_STYLE}]")


def print_info(message: str):
    """Print an info/progress message using the configured style."""
    console = Console()
    console.print(f"[{INFO_STYLE}]{message}[/{INFO_STYLE}]")


def handle_http_error(e: requests.HTTPError):
    """Handle HTTP errors by printing a user-friendly message."""
    if e.response.status_code == 401 or e.response.status_code == 403:
        print_error("Unauthorized. Please sign in with `prim signin`.")
    else:
        try:
            detail = e.response.json().get("detail", e.response.text)
            print_error(detail)
        except requests.exceptions.JSONDecodeError:
            print_error(str(e))


def get_authenticated_session() -> requests.Session:
    """Get an authenticated session."""
    session = requests.Session()
    cookie = load_cookie()
    if cookie:
        session.headers["Cookie"] = cookie
    return session


def get_agent(session: requests.Session, name_or_id: str):
    """Get an agent by name or ID."""
    try:
        # Only try direct ID lookup if the input looks like a UUID
        if is_uuid(name_or_id):
            response = session.get(f"{API_BASE_URL}/v1/agents/{name_or_id}")
            if response.status_code == 200:
                agent = response.json().get("data")
                if agent:
                    return agent

        # If not found by ID or not a UUID, get all agents and search by name
        response = session.get(f"{API_BASE_URL}/v1/agents?")
        response.raise_for_status()
        agents = response.json()["data"]
        name = name_or_id.lower()
        agent = next(
            (a for a in agents if a.get("name", "").lower() == name), 
            None
        )
        if not agent:
            print_error(f"Agent with name or ID '{name_or_id}' not found.")
            return None
        return agent
    except requests.HTTPError as e:
        handle_http_error(e)
        return None


def get_voice(session: requests.Session, name_or_id: str):
    """Get a voice by name or ID."""
    try:
        # Only try direct ID lookup if the input looks like a UUID
        if is_uuid(name_or_id):
            response = session.get(
                f"{API_BASE_URL}/v1/voices/{name_or_id}"
            )  # TODO: causes 403 Forbidden error even though it's a valid ID
            if response.status_code == 200:
                voice = response.json().get("data")
                if voice:
                    return voice

        # If not found by ID or not a UUID, get all voices and search by name
        response = session.get(f"{API_BASE_URL}/v1/voices?")
        response.raise_for_status()
        voices = response.json()["data"]
        name = name_or_id.lower()
        voice = next(
            (
                v
                for v in voices
                if v.get("name", "").lower() == name or v.get("id", "") == name_or_id
            ),
            None,
        )
        if not voice:
            print_error(f"Voice with name or ID '{name_or_id}' not found.")
            return None
        return voice
    except requests.HTTPError as e:
        handle_http_error(e)
        return None


def is_uuid(uuid_string):
    """Check if a string looks like a UUID."""
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", 
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


def get_function(
    session: requests.Session, 
    agent_id: str, 
    function_name_or_id: str
):
    """Get a function by name or ID."""
    try:
        # Only try direct ID lookup if the input looks like a UUID
        if is_uuid(function_name_or_id):
            response = session.get(
                f"{API_BASE_URL}/v1/agents/{agent_id}/functions/{function_name_or_id}"
            )
            if response.status_code == 200:
                function = response.json().get("data")
                if function:
                    return function

        # If not found by ID or not a UUID, get all functions and search by name
        response = session.get(
            f"{API_BASE_URL}/v1/agents/{agent_id}/functions?filters[agentId]={agent_id}"
        )
        response.raise_for_status()
        functions = response.json()["data"]
        function = next(
            (f for f in functions if f.get("name") == function_name_or_id), 
            None
        )
        if not function:
            print_error(
                f"Function with name or ID '{function_name_or_id}' not found."
            )
            return None
        return function
    except requests.HTTPError as e:
        handle_http_error(e)
        return None


def get_environment(
    session: requests.Session, 
    agent_id: str, 
    env_name_or_id: str
):
    """Get an environment by name or ID."""
    try:
        # Only try direct ID lookup if the input looks like a UUID
        if is_uuid(env_name_or_id):
            response = session.get(
                f"{API_BASE_URL}/v1/agents/{agent_id}/environments/{env_name_or_id}"
            )
            if response.status_code == 200:
                env = response.json().get("data")
                if env:
                    return env

        # If not found by ID or not a UUID, get all environments and search by name
        response = session.get(
            f"{API_BASE_URL}/v1/agents/{agent_id}/environments?filters[agentId]={agent_id}"
        )
        response.raise_for_status()
        envs = response.json()["data"]
        env = next(
            (e for e in envs if e.get("name") == env_name_or_id), 
            None
        )
        if not env:
            print_error(
                f"Environment with name or ID '{env_name_or_id}' not found."
            )
            return None
        return env
    except requests.HTTPError as e:
        handle_http_error(e)
        return None


def manage_variables(
    session: requests.Session, 
    agent_id: str, 
    env_id: str, 
    is_update: bool
):
    """Manage variables for an environment."""
    if is_update:
        response = session.get(
            f"{API_BASE_URL}/v1/agents/{agent_id}/environments/{env_id}/variables"
            f"?filters[agentId]={agent_id}&filters[environmentId]={env_id}"
        )
        response.raise_for_status()
        variables = response.json()["data"]
        for var in variables:
            if confirm(f"Update variable '{var['name']}'?", default=False):
                if confirm(f"Delete variable '{var['name']}'?", default=False):
                    delete_response = session.delete(
                        f"{API_BASE_URL}/v1/agents/{agent_id}/environments/{env_id}/variables/{var['id']}"
                    )
                    delete_response.raise_for_status()
                    print_success(f"Variable '{var['name']}' deleted.")
                    continue
                name = prompt("New name", default=var["name"])
                value = prompt(
                    "New value", 
                    default="*****" if var.get("masked") else var["value"]
                )
                masked = confirm("Mask value?", default=var.get("masked", False))
                updated_var = {"name": name, "value": value, "masked": masked}
                patch_response = session.patch(
                    f"{API_BASE_URL}/v1/agents/{agent_id}/environments/{env_id}/variables/{var['id']}",
                    json=updated_var,
                )
                patch_response.raise_for_status()
                print_success(f"Variable '{name}' updated.")

    while confirm("Add a new variable?", default=False):
        name = prompt("Variable name")
        value = prompt("Variable value")
        masked = confirm("Mask value?", default=False)
        new_var = {
            "name": name,
            "value": value,
            "masked": masked,
            "agentEnvironmentId": env_id,
            "agentId": agent_id,
        }
        post_response = session.post(
            f"{API_BASE_URL}/v1/agents/{agent_id}/environments/{env_id}/variables",
            json=new_var,
        )
        post_response.raise_for_status()
        print_success(f"Variable '{name}' added.")


def create_venv(directory_path: str):
    """Create a virtual environment in the directory using uv and install requirements."""
    # Convert to absolute path
    directory_path = os.path.abspath(directory_path)
    venv_path = os.path.join(directory_path, ".venv")
    pyproject_path = os.path.join(directory_path, "pyproject.toml")
    requirements_path = os.path.join(directory_path, "requirements.txt")

    # Check if .venv already exists
    if os.path.exists(venv_path):
        print_info(f"Virtual environment already exists at {venv_path}")
        return

    try:
        # First check for pyproject.toml and use uv sync
        if os.path.exists(pyproject_path):
            print_info(
                f"Found pyproject.toml, creating virtual environment with uv sync"
            )

            # Use uv sync to create virtual environment and install dependencies
            result = subprocess.run(
                ["uv", "sync", "--python", "3.11"],
                capture_output=True,
                text=True,
                cwd=directory_path,
            )

            if result.returncode != 0:
                print_error(
                    f"Failed to create virtual environment with uv sync: {result.stderr}"
                )
                return

            print_success(
                f"Virtual environment created and dependencies installed in {venv_path}"
            )
            return

        # Fall back to requirements.txt if pyproject.toml doesn't exist
        elif os.path.exists(requirements_path):
            print_info(
                f"Found requirements.txt, creating virtual environment with uv pip"
            )

            # First create the virtual environment
            print_info(f"Creating virtual environment in {venv_path}")
            result = subprocess.run(
                ["uv", "venv", venv_path],
                capture_output=True,
                text=True,
                cwd=directory_path,
            )

            if result.returncode != 0:
                print_error(f"Failed to create virtual environment: {result.stderr}")
                return

            # Get the Python interpreter path in the virtual environment
            if os.name == "nt":  # Windows
                python_path = os.path.join(venv_path, "Scripts", "python.exe")
            else:  # Unix/Linux/macOS
                python_path = os.path.join(venv_path, "bin", "python")

            # Install requirements using uv pip with the virtual environment's Python
            print_info("Installing dependencies from requirements.txt")
            result = subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    "-r",
                    "requirements.txt",
                    "--python",
                    python_path,
                ],
                capture_output=True,
                text=True,
                cwd=directory_path,
            )

            if result.returncode != 0:
                print_error(f"Failed to install dependencies: {result.stderr}")
                return

            print_success(
                f"Virtual environment created and dependencies installed in {venv_path}"
            )
        else:
            print_info(
                f"No pyproject.toml or requirements.txt found in {directory_path}, "
                f"skipping virtual environment creation."
            )
            return

    except FileNotFoundError:
        print_error(
            "uv is not installed. Please install uv first: "
            "https://docs.astral.sh/uv/getting-started/installation/"
        )
    except Exception as e:
        print_error(f"Error creating virtual environment: {str(e)}")


def get_lang(directory_path: str):
    """Get the language of the function code."""
    handler_file = next(
        (f for f in os.listdir(directory_path) if f.startswith("handler.")),
        "handler.py",
    )
    ext = os.path.splitext(handler_file)[-1].lstrip(".")
    return EXT_TO_LANG.get(ext, "python")


def package_function(directory_path: str):
    """Create a zip file of the directory"""
    # Convert to absolute path and ensure it exists
    directory_path = os.path.abspath(directory_path)

    lang = get_lang(directory_path)

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory '{directory_path}' does not exist")

    # create_venv(directory_path)

    # Create zip file path in the same directory as the source
    zip_filename = f"{os.path.basename(directory_path)}.zip"
    zip_path = os.path.join(os.path.dirname(directory_path), zip_filename)

    # Define files and directories to exclude
    exclude_patterns = [
        ".venv",  # Virtual environment
        "__pycache__",  # Python cache
        ".pyc",  # Compiled Python files
        ".DS_Store",  # macOS system files
        "Thumbs.db",  # Windows system files
        ".git",  # Git directory
        ".gitignore",  # Git ignore file
        "*.zip",  # Existing zip files
    ]

    def should_exclude(path):
        """Check if a path should be excluded from the zip."""
        basename = os.path.basename(path)
        for pattern in exclude_patterns:
            if pattern.startswith("*"):
                # Handle wildcard patterns
                if path.endswith(pattern[1:]):
                    return True
            elif basename == pattern:
                return True
        return False

    # Create the zip file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(d)]

            for file in files:
                file_path = os.path.join(root, file)

                # Skip excluded files
                if should_exclude(file_path):
                    continue

                # Calculate relative path for the archive
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname=arcname)

    return os.path.abspath(zip_path), lang


def not_empty(value: str) -> str:
    """Check if a value is not empty."""
    if not value or not value.strip():
        raise typer.BadParameter("Value cannot be empty.")
    return value


def prompt(
    message: str, 
    default=None, 
    validation=not_empty, 
    **kwargs
):
    """Prompt for input with validation (default: not_empty) and consistent style."""
    return typer.prompt(
        message, 
        default=default, 
        value_proc=validation, 
        **kwargs
    )


def confirm(
    message: str, 
    default=None, 
    validation=None, 
    **kwargs
):
    """Prompt for confirmation with consistent style (no validation by default)."""
    return typer.confirm(message, default=default, **kwargs)
