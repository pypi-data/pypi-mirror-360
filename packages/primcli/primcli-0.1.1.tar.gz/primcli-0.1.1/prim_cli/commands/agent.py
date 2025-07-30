import typer

from ..entities.agent import Agent, AgentRepository
from rich.console import Console
from rich.table import Table

from ..commands.env import app as env_app
from ..commands.func import app as func_app
from ..utils.config import (
    ID_STYLE,
    TITLE_STYLE,
    UNNAMED,
    NOT_AVAILABLE,
)
from ..utils.utils import (
    format_date,
    get_authenticated_session,
    get_voice,
    print_success,
    print_info,
    print_error,
    prompt,
    confirm,
)

app = typer.Typer()
app.add_typer(func_app, name="func", help="Commands for managing agent functions.")
app.add_typer(env_app, name="env", help="Commands for managing agent environments.")

console = Console()
agent_repository = AgentRepository()


@app.command("list")
def agents_list(
    all: bool = typer.Option(
        False, "--all", help="Show detailed information for all agents."
    ),
):
    """List all agents. Use --all to show detailed information."""
    print_info("Searching for agents...")

    agents = agent_repository.get()
    if not agents:
        print_error("No agents found.")
        return

    print_success(f"Found {len(agents)} agents")

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
            table.add_row(
                agent.name or UNNAMED,
                format_date(agent.created_at),
                format_date(agent.updated_at),
                f"[{ID_STYLE}]{agent.id}[/{ID_STYLE}]",
            )
    else:
        table = Table("Name", "Updated", show_header=True, header_style=TITLE_STYLE)

        for agent in agents:
            table.add_row(
                agent.name or UNNAMED,
                format_date(agent.updated_at),
            )

    console.print(table)


@app.command("info")
def agent_info(name_or_id: str = typer.Argument(..., help="Agent name or ID.")):
    """Show detailed information about an agent. Provide agent name or ID."""

    agent = agent_repository.get_by_name_or_id(name_or_id)
    if not agent:
        print_error(f"Agent with name or ID '{name_or_id}' not found.")
        return

    voice_name = NOT_AVAILABLE
    if agent.default_voice_id:
        session = get_authenticated_session()
        voice = get_voice(session, agent.default_voice_id)
        if voice:
            voice_name = voice.get("name", "") or UNNAMED

    table = Table(show_header=False, show_lines=False, box=None, pad_edge=False)
    table.add_row(
        f"[{TITLE_STYLE}]Agent[/{TITLE_STYLE}]",
        f"{agent.name or UNNAMED}",
    )
    table.add_row(
        f"[{TITLE_STYLE}]ID[/{TITLE_STYLE}]",
        f"[{ID_STYLE}]{agent.id}[/{ID_STYLE}]",
    )
    table.add_row(
        f"[{TITLE_STYLE}]Created[/{TITLE_STYLE}]",
        f"{format_date(agent.created_at)}",
    )
    table.add_row(
        f"[{TITLE_STYLE}]Updated[/{TITLE_STYLE}]",
        f"{format_date(agent.updated_at)}",
    )
    table.add_row(
        f"[{TITLE_STYLE}]Deleted[/{TITLE_STYLE}]",
        f"{format_date(agent.deleted_at) or NOT_AVAILABLE}",
    )
    table.add_row(f"[{TITLE_STYLE}]Voice[/{TITLE_STYLE}]", voice_name)
    table.add_row(
        f"[{TITLE_STYLE}]Description[/{TITLE_STYLE}]",
        f"{agent.description}",
    )
    console.print(table)


@app.command("create")
def agent_create():
    """Create a new agent. You will be prompted for name, description, and voice."""
    agent = Agent()
    agent.name = prompt("Enter agent name")
    agent.description = prompt("Enter agent description")

    voice = None
    while not voice:
        voice_name_or_id = prompt("Enter voice name or ID", default="", validation=None)
        if not voice_name_or_id:
            voice = None
            break

        session = get_authenticated_session()
        voice = get_voice(session, voice_name_or_id)
        if voice:
            agent.default_voice_id = voice["id"]

    created_agent = agent_repository.create(agent)

    if created_agent:
        print_success("Agent created successfully!")
    else:
        print_error("Failed to create agent.")


@app.command("update")
def agent_update(name_or_id: str = typer.Argument(..., help="Agent name or ID.")):
    """Update an existing agent. Provide agent name or ID."""
    agent = agent_repository.get_by_name_or_id(name_or_id)
    if not agent:
        print_error(f"Agent with name or ID '{name_or_id}' not found.")
        return

    session = get_authenticated_session()
    current_voice_name = ""
    if agent.default_voice_id:
        current_voice = get_voice(session, agent.default_voice_id)
        if current_voice:
            current_voice_name = current_voice.get("name")

    agent.name = prompt("Enter new agent name", default=agent.name)
    agent.description = prompt("Enter new agent description", default=agent.description)

    voice_name_or_id = prompt(
        "Enter new voice name or ID", default=current_voice_name, validation=None
    )
    voice = get_voice(session, voice_name_or_id)
    if voice:
        agent.default_voice_id = voice["id"]

    updated_agent = agent_repository.update_by_id(agent.id, agent)

    if updated_agent:
        print_success("Agent updated successfully!")
    else:
        print_error("Failed to update agent.")


@app.command("delete")
def agent_delete(name_or_id: str = typer.Argument(..., help="Agent name or ID.")):
    """Delete an existing agent. Provide agent name or ID."""
    agent = agent_repository.get_by_name_or_id(name_or_id)
    if not agent:
        print_info(f"Unable to find agent by name or id: {name_or_id}")
        return

    if confirm(f"Are you sure you want to delete agent '{agent.name}'?"):
        is_deleted = agent_repository.delete_by_id(agent.id)
        if is_deleted:
            print_success(f"Agent '{agent.name}' deleted successfully.")
        else:
            print_error(f"Failed to delete agent '{agent.name}'.")
