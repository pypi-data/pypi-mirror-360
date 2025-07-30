import requests
import typer
import webbrowser

from rich.console import Console
from rich.table import Table

from ..commands.env import app as env_app
from ..commands.func import app as func_app
from ..utils.config import (
    API_BASE_URL,
    ID_STYLE,
    TITLE_STYLE,
    UNNAMED,
    NOT_AVAILABLE,
)
from ..utils.utils import (
    format_date,
    get_agent,
    get_authenticated_session,
    get_voice,
    handle_http_error,
    print_success,
    print_info,
    prompt,
    confirm,
)

app = typer.Typer()
app.add_typer(func_app, name="func", help="Commands for managing agent functions.")
app.add_typer(env_app, name="env", help="Commands for managing agent environments.")


@app.command("list")
def agents_list(
    all: bool = typer.Option(
        False, "--all", help="Show detailed information for all agents."
    )
):
    """List all agents. Use --all to show detailed information."""
    print_info("Searching for agents...")
    try:
        session = get_authenticated_session()
        response = session.get(f"{API_BASE_URL}/v1/agents?")
        response.raise_for_status()
        n = response.json()["metadata"]["total"]
        console = Console()
        print_success(f"Found {n} agents")
        agents = response.json()["data"]
        table = None
        if all:
            table = Table(
                "Name",
                "Created",
                "Updated",
                "ID",
                show_header=True,
                header_style=TITLE_STYLE,
            )
            for agent in agents:
                name = agent.get("name", "") or UNNAMED
                created = format_date(agent.get("createdAt", ""))
                updated = format_date(agent.get("updatedAt", ""))
                agent_id = agent.get("id", "")
                table.add_row(
                    name,
                    created,
                    updated,
                    f"[{ID_STYLE}]{agent_id}[/{ID_STYLE}]",
                )
        else:
            table = Table("Name", "Updated", show_header=True, header_style=TITLE_STYLE)
            for agent in agents:
                name = agent.get("name", "") or UNNAMED
                updated = format_date(agent.get("updatedAt", ""))
                table.add_row(
                    name,
                    updated,
                )
        console.print(table)
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("info")
def agent_info(name_or_id: str = typer.Argument(..., help="Agent name or ID.")):
    """Show detailed information about an agent. Provide agent name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, name_or_id)
        if not agent:
            return

        voice_name = NOT_AVAILABLE
        if agent.get("defaultVoiceId"):
            voice = get_voice(session, agent.get("defaultVoiceId"))
            if voice:
                voice_name = voice.get("name", "") or UNNAMED

        console = Console()
        table = Table(show_header=False, show_lines=False, box=None, pad_edge=False)
        table.add_row(
            f"[{TITLE_STYLE}]Agent[/{TITLE_STYLE}]",
            f"{agent.get('name', '') or UNNAMED}",
        )
        table.add_row(
            f"[{TITLE_STYLE}]ID[/{TITLE_STYLE}]",
            f"[{ID_STYLE}]{agent.get('id', '')}[/{ID_STYLE}]",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Created[/{TITLE_STYLE}]",
            f"{format_date(agent.get('createdAt', ''))}",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Updated[/{TITLE_STYLE}]",
            f"{format_date(agent.get('updatedAt', ''))}",
        )
        table.add_row(
            f"[{TITLE_STYLE}]Deleted[/{TITLE_STYLE}]",
            f"{format_date(agent.get('deletedAt', '')) or NOT_AVAILABLE}",
        )
        table.add_row(f"[{TITLE_STYLE}]Voice[/{TITLE_STYLE}]", voice_name)
        table.add_row(
            f"[{TITLE_STYLE}]Description[/{TITLE_STYLE}]",
            f"{agent.get('description', '')}",
        )
        console.print(table)
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("create")
def agent_create():
    """Create a new agent. You will be prompted for name, description, and voice."""
    try:
        session = get_authenticated_session()
        name = prompt("Enter agent name")
        description = prompt("Enter agent description")
        voice = None
        while not voice:
            voice_name_or_id = prompt(
                "Enter voice name or ID", default="", validation=None
            )
            if not voice_name_or_id:
                voice = None
                break
            voice = get_voice(session, voice_name_or_id)

        response = session.post(
            f"{API_BASE_URL}/v1/agents",
            json={
                "name": name,
                "description": description,
                "defaultVoiceId": voice["id"] if voice else None,
            },
        )
        response.raise_for_status()
        print_success("Agent created successfully!")
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("update")
def agent_update(name_or_id: str = typer.Argument(..., help="Agent name or ID.")):
    """Update an existing agent. Provide agent name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, name_or_id)
        if not agent:
            return

        current_voice_name = NOT_AVAILABLE
        if agent.get("defaultVoiceId"):
            current_voice = get_voice(session, agent.get("defaultVoiceId"))
            if current_voice:
                current_voice_name = current_voice.get("name", NOT_AVAILABLE)

        new_name = prompt("Enter new agent name", default=agent.get("name", ""))
        new_description = prompt(
            "Enter new agent description", default=agent.get("description", "")
        )

        new_voice = None
        while not new_voice:
            voice_name_or_id = prompt(
                "Enter new voice name or ID", default=current_voice_name
            )
            new_voice = get_voice(session, voice_name_or_id)

        updated_agent_data = {
            "name": new_name,
            "description": new_description,
            "defaultVoiceId": new_voice["id"],
        }

        response = session.patch(
            f"{API_BASE_URL}/v1/agents/{agent['id']}", json=updated_agent_data
        )
        response.raise_for_status()
        print_success("Agent updated successfully")
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("delete")
def agent_delete(name_or_id: str = typer.Argument(..., help="Agent name or ID.")):
    """Delete an existing agent. Provide agent name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, name_or_id)
        if not agent:
            return
        if confirm(f"Are you sure you want to delete agent '{agent['name']}'?"):
            session.delete(f"{API_BASE_URL}/v1/agents/{agent['id']}")
            print_success(f"Agent '{agent['name']}' deleted successfully.")
    except requests.HTTPError as e:
        handle_http_error(e)
