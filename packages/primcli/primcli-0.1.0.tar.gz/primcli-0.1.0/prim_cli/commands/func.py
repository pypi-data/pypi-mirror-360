import os
import tempfile
from datetime import datetime
from pathlib import Path
import base64

import requests
import typer
from rich.console import Console
from rich.table import Table

from ..utils.config import (
    API_BASE_URL,
    EXT_TO_LANG,
    TITLE_STYLE,
    ID_STYLE,
    PATH_STYLE,
    UNNAMED,
    NOT_AVAILABLE,
)
from ..utils.utils import (
    format_date,
    get_agent,
    get_authenticated_session,
    get_environment,
    handle_http_error,
    get_function,
    package_function,
    print_success,
    print_error,
    print_warning,
    print_info,
    prompt,
    confirm,
)
from .debug import run_debugger

app = typer.Typer()

# TODO: fix error handling so it doesn't say success when it fails


@app.command("list")
def func_list(agent_name_or_id: str = typer.Argument(..., help="Agent name or ID.")):
    """List all functions for an agent. Provide agent name or ID."""
    try:
        print_info(f"Getting functions for {agent_name_or_id}...")
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        response = session.get(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/functions?filters[agentId]={agent['id']}"
        )
        response.raise_for_status()
        data = response.json()["data"]
        table = Table(
            "Name",
            "Language",
            "Updated",
            "ID",
            show_header=True,
            header_style=TITLE_STYLE,
        )
        for func in data:
            table.add_row(
                f"{func['name']}",
                f"{func.get('language', NOT_AVAILABLE)}",
                f"{format_date(func['updatedAt'])}",
                f"[{ID_STYLE}]{func['id']}[/{ID_STYLE}]",
            )
        console = Console()
        console.print(table)
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("info")
def func_info(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID."),
    function_name_or_id: str = typer.Argument(..., help="Function name or ID."),
):
    """Show detailed information about a function. Provide agent name or ID and function name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return

        function = get_function(session, agent["id"], function_name_or_id)
        if not function:
            return

        console = Console()
        table = Table(show_header=False, show_lines=False, box=None, pad_edge=False)
        table.add_row(
            f"[{TITLE_STYLE}]Function[/{TITLE_STYLE}]",
            f"{function.get('name', '') or UNNAMED}",
        )
        table.add_row(
            f"[{TITLE_STYLE}]ID[/{TITLE_STYLE}]",
            f"[{ID_STYLE}]{function.get('id', '')}[/{ID_STYLE}]",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Agent[/{TITLE_STYLE}]",
            f"{agent.get('name', '') or UNNAMED}",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Agent ID[/{TITLE_STYLE}]",
            f"[{ID_STYLE}]{agent.get('id', '')}[/{ID_STYLE}]",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Created[/{TITLE_STYLE}]",
            f"{format_date(function.get('createdAt', ''))}",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Updated[/{TITLE_STYLE}]",
            f"{format_date(function.get('updatedAt', ''))}",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Deleted[/{TITLE_STYLE}]",
            f"{format_date(function.get('deletedAt', '')) or NOT_AVAILABLE}",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Language[/{TITLE_STYLE}]",
            f"{function.get('language', '')}",
        )
        console.print(table)

        if confirm("View function code?", default=False):
            code = function.get("code", "")
            if code:
                # Check if this is zip bytes or plain text
                is_zip = function.get("codePath") is not None

                if is_zip:
                    print_info(
                        "This function uses zip file storage. The code is stored as base64-encoded zip bytes."
                    )
                    if confirm("Save zip file to disk?", default=False):
                        zip_filename = f"function_{function.get('id', 'unknown')}.zip"
                        try:
                            zip_bytes = base64.b64decode(code)
                            with open(zip_filename, "wb") as f:
                                f.write(zip_bytes)
                            print_info(
                                f"Zip file saved as: [{PATH_STYLE}]{zip_filename}[/{PATH_STYLE}]"
                            )
                        except Exception as e:
                            print_error(f"Failed to save zip file: {e}")
                else:
                    print_info("This function uses plain text storage.")
                    language = function.get("language", "").lower()
                    ext = next(
                        (k for k, v in EXT_TO_LANG.items() if v.lower() == language),
                        language or "txt",
                    )
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=f".{ext}", mode="w", encoding="utf-8"
                    ) as tmp:
                        tmp.write(code)
                        tmp_path = tmp.name
                    print_info(
                        f"Temporary file created at: [{PATH_STYLE}]{tmp_path}[/{PATH_STYLE}]"
                    )
                    if confirm("Remove temporary file?", default=True):
                        os.remove(tmp_path)
            else:
                print_warning("No code found for this function.")
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("create")
def func_create(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID."),
    directory: str = typer.Argument(..., help="Directory path to the function code."),
):
    """Create a new function for an agent. Provide agent name or ID and file path to the function code zip file."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return

        directory_full_path = Path(directory).expanduser()
        if not directory_full_path.exists():
            print_error(
                f"File not found at '[{PATH_STYLE}]{directory_full_path}[/{PATH_STYLE}]'"
            )
            return

        zip_file_path, code_lang = package_function(directory_full_path)

        # Read the zip file as bytes and encode as base64
        with open(zip_file_path, "rb") as f:
            zip_bytes = f.read()
            code = base64.b64encode(zip_bytes).decode("utf-8")

        timestamp = datetime.now().isoformat()
        data = {
            "agentId": agent["id"],
            "code": code,  # This is now base64-encoded zip bytes
            "isMultifile": True,
            "language": code_lang,
            "updatedAt": timestamp,
            "createdAt": timestamp,
            "deletedAt": None,
        }
        response = session.post(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/functions", json=data
        )
        response.raise_for_status()
        os.remove(zip_file_path)
        print_success(
            f"Function '{response.json()['data']['name']}' created successfully."
        )
    except (requests.HTTPError, FileNotFoundError) as e:
        if isinstance(e, requests.HTTPError):
            handle_http_error(e)
        else:
            print_error(str(e))


@app.command("update")
def func_update(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID"),
    function_name_or_id: str = typer.Argument(..., help="Function name or ID"),
    directory: str = typer.Option(
        None, "--dir", help="Directory path to the function code"
    ),
):
    """Update a function. Provide agent name or ID. Provide function name or ID. Optionally provide file path to the function code zip file."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return

        function = get_function(session, agent["id"], function_name_or_id)
        if not function:
            return
        name = function.get("name", "")
        if not directory:
            name = prompt("Enter function name", default=name)
            print_info(
                "You need to provide a directory path for the updated function code."
            )
            directory = prompt("Enter directory path")
        # else:
        #     directory = Path(directory).expanduser()
        directory = Path(directory).expanduser()
        if not directory.exists():
            print_error(
                f"Directory not found at '[{PATH_STYLE}]{directory}[/{PATH_STYLE}]'"
            )
            return

        zip_file_path, code_lang = package_function(directory)

        # Read the zip file as bytes and encode as base64
        with open(zip_file_path, "rb") as f:
            zip_bytes = f.read()
            code = base64.b64encode(zip_bytes).decode("utf-8")

        updated_data = {
            "name": name,
            "code": code,  # This is now base64-encoded zip bytes
            "language": code_lang,
            "updatedAt": datetime.now().isoformat(),
        }
        response = session.patch(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/functions/{function['id']}",
            json=updated_data,
        )
        response.raise_for_status()
        os.remove(zip_file_path)
        print_success(f"Function '{name}' updated successfully")
    except requests.HTTPError as e:
        print_error(str(e))


@app.command("delete")
def func_delete(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID."),
    function_name_or_id: str = typer.Argument(..., help="Function name or ID."),
):
    """Delete a function. Provide agent name or ID and function name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return

        function = get_function(session, agent["id"], function_name_or_id)
        if not function:
            return

        if confirm(f"Are you sure you want to delete function '{function['name']}'?"):
            response = session.delete(
                f"{API_BASE_URL}/v1/agents/{agent['id']}/functions/{function['id']}"
            )
            response.raise_for_status()
            print_success(f"Function '{function['name']}' deleted successfully.")
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("deploy")
def func_deploy(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID"),
    function_name_or_id: str = typer.Argument(..., help="Function name or ID"),
    env_name_or_id: str = typer.Option(None, "--env", help="Environment name or ID"),
):
    """Deploy a function to an environment. Provide agent name or ID and function name or ID. Optionally provide environment name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return

        function = get_function(session, agent["id"], function_name_or_id)
        if not function:
            return
        if env_name_or_id or confirm(f"Deploy function to environment?", default=False):
            while True:
                env = env_name_or_id or prompt("Enter environment name or ID")
                env_data = get_environment(session, agent["id"], env)
                if env_data:
                    env = env_data.get("id", "")
                    break
                env_name_or_id = None
        else:
            return
        data = {
            "agentId": agent["id"],
            "functionId": function["id"],
            "environmentId": env_data["id"],
        }
        if not confirm(
            f"Deploy function '{function['name']}' to environment '{env_data['name']}'?",
            default=True,
        ):
            return
        response = session.patch(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/environments/{env_data['id']}",
            json=data,
        )
        response.raise_for_status()
        print_success(
            f"Function '{function['name']}' deployed to environment '{env_data['name']}' successfully."
        )
    except requests.HTTPError as e:
        handle_http_error(e)
