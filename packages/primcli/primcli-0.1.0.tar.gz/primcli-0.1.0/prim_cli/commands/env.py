from datetime import datetime

import requests
import typer
from rich.console import Console
from rich.table import Table
import asyncio

from ..utils.config import (
    API_BASE_URL,
    TITLE_STYLE,
    TRUE_STYLE,
    FALSE_STYLE,
    ID_STYLE,
    UNNAMED,
    NOT_AVAILABLE
)
from ..utils.utils import (
    format_date,
    get_agent,
    get_authenticated_session,
    get_function,
    handle_http_error,
    get_environment,
    manage_variables,
    print_success,
    print_info,
    print_warning,
    prompt,
    confirm
)
from .debug import run_debugger

app = typer.Typer()


@app.command("list")
def agent_env_list(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID.")
):
    """List all environments for an agent. Provide agent name or ID."""
    try:
        print_info(f"Getting environments for {agent_name_or_id}...")
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        response = session.get(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/environments?filters[agentId]={agent['id']}"
        )
        response.raise_for_status()
        data = response.json()["data"]
        table = Table(
            "Name", "Phone", "Function", "Updated", "ID",
            show_header=True, header_style=TITLE_STYLE
        )
        functions = session.get(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/functions?filters[agentId]={agent['id']}"
        ).json()["data"]
        for env in data:
            func_name = next(
                (f["name"] for f in functions if f["id"] == env["functionId"]), ""
            )
            table.add_row(
                f"{env['name']}",
                f"{env.get('phoneNumber', NOT_AVAILABLE)}",
                f"{func_name or NOT_AVAILABLE}",
                f"{format_date(env['updatedAt'])}",
                f"[{ID_STYLE}]{env['id']}[/{ID_STYLE}]",
            )
        console = Console()
        console.print(table)
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("info")
def agent_env_info(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID."),
    env_name_or_id: str = typer.Argument(..., help="Environment name or ID."),
):
    """Show detailed information about an environment. Provide agent name or ID and environment name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        env = get_environment(session, agent["id"], env_name_or_id)
        if not env:
            return
        if env["functionId"]:
            func = get_function(session, agent["id"], env["functionId"])
            if not func:
                return
        else:
            func = None

        console = Console()
        table = Table(
            show_header=False, 
            show_lines=False, 
            box=None, 
            pad_edge=False
        )
        table.add_row(
            f"[{TITLE_STYLE}]Environment[/{TITLE_STYLE}]", 
            f"{env.get('name', '') or UNNAMED}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]ID[/{TITLE_STYLE}]", 
            f"[{ID_STYLE}]{env.get('id', '')}[/{ID_STYLE}]"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Agent[/{TITLE_STYLE}]", 
            f"{agent.get('name', '') or UNNAMED}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Agent ID[/{TITLE_STYLE}]", 
            f"[{ID_STYLE}]{agent.get('id', '')}[/{ID_STYLE}]"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Function[/{TITLE_STYLE}]", 
            f"{func.get('name', '') if func else NOT_AVAILABLE}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Function ID[/{TITLE_STYLE}]", 
            f"[{ID_STYLE}]{func.get('id', '') if func else NOT_AVAILABLE}[/{ID_STYLE}]"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Created[/{TITLE_STYLE}]", 
            f"{format_date(env.get('createdAt', ''))}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Updated[/{TITLE_STYLE}]", 
            f"{format_date(env.get('updatedAt', ''))}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Deleted[/{TITLE_STYLE}]", 
            f"{format_date(env.get('deletedAt', '')) or NOT_AVAILABLE}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Phone[/{TITLE_STYLE}]", 
            f"{env.get('phoneNumber', '') or NOT_AVAILABLE}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Recording[/{TITLE_STYLE}]", 
            f"[{TRUE_STYLE}]On[/{TRUE_STYLE}]" if env.get('recording', False) 
            else f"[{FALSE_STYLE}]Off[/{FALSE_STYLE}]"
        )
        table.add_row(
            f"[{TITLE_STYLE}]Redaction[/{TITLE_STYLE}]", 
            f"[{TRUE_STYLE}]On[/{TRUE_STYLE}]" if env.get('redaction', False) 
            else f"[{FALSE_STYLE}]Off[/{FALSE_STYLE}]"
        )
        table.add_row(
            f"[{TITLE_STYLE}]STT Language[/{TITLE_STYLE}]", 
            f"{'English' if env.get('sttLanguage', '') == 'en' else env.get('sttLanguage', '') or NOT_AVAILABLE}"
        )
        table.add_row(
            f"[{TITLE_STYLE}]STT Keywords[/{TITLE_STYLE}]", 
            f"{env.get('sttPrompt', '') or NOT_AVAILABLE}"
        )
        vars_response = session.get(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/environments/{env['id']}/variables"
            f"?filters[agentId]={agent['id']}&filters[environmentId]={env['id']}"
        ).json()["data"]
        if vars_response:
            table.add_row(f"[{TITLE_STYLE}]Variables[/{TITLE_STYLE}]", "")
            vars_table = Table(
                "Name", "Value", "Masked", 
                show_header=True, 
                header_style=TITLE_STYLE, 
                box=None, 
                show_edge=False
            )
            for var in vars_response:
                masked = var.get("masked", False)
                value = "*****" if masked else var.get("value", "")
                vars_table.add_row(
                    var.get("name", UNNAMED),
                    value,
                    f"[{TRUE_STYLE}]Yes[/{TRUE_STYLE}]" if masked 
                    else f"[{FALSE_STYLE}]No[/{FALSE_STYLE}]"
                )
            table.add_row("", vars_table)
        console.print(table)
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("create")
def agent_env_create(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID.")
):
    """Create a new environment for an agent. Provide agent name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        env_name = prompt("Enter environment name")
        phone = prompt("Enter phone number", default=NOT_AVAILABLE)
        if phone == "N/A":
            phone = None
        recording = confirm("Enable recording?", default=False)
        redaction = confirm("Enable redaction?", default=False)
        stt_language_is_english = confirm(
            "Use English for STT language? (select No for Multi-Lingual)", 
            default=True
        )
        stt_language = "en" if stt_language_is_english else "multi"
        stt_prompt = prompt(
            "Enter STT keywords (comma-separated)", 
            default="", 
            validation=None
        )
        deploy = confirm("Deploy function to environment?", default=False)
        if deploy:
            while True:
                func = prompt("Function (name or ID)")
                func_data = get_function(session, agent["id"], func)
                if func_data:
                    func = func_data.get("id", "")
                    break
        else:
            func = ""
        new_env = {
            "name": env_name,
            "agentId": agent["id"],
            "functionId": func,
            "phoneNumber": phone,
            "recordingEnabled": recording,
            "redactionEnabled": redaction,
            "sttLanguage": stt_language,
            "sttPrompt": stt_prompt,
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "deletedAt": None,
        }
        response = session.post(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/environments", 
            json=new_env
        )
        env = response.json()["data"]
        response.raise_for_status()
        manage_variables(session, agent["id"], env["id"], False)
        print_success(
            f"Environment '{env_name}' created successfully (ID: '{env['id']}')"
        )
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("update")
def agent_env_update(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID"),
    env_name_or_id: str = typer.Argument(..., help="Environment name or ID"),
):
    """Update an environment. Provide agent name or ID and environment name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        env = get_environment(session, agent["id"], env_name_or_id)
        if not env:
            return
        env_name = prompt(
            "Enter new environment name", 
            default=env.get("name", "")
        )
        phone = prompt(
            "Enter new phone number",
            default=env.get("phoneNumber", "") or NOT_AVAILABLE,
        )
        if phone == "N/A":
            phone = None
        recording = confirm(
            "Enable recording?", 
            default=env.get("recordingEnabled", False)
        )
        redaction = confirm(
            "Enable redaction?", 
            default=env.get("redactionEnabled", False)
        )
        stt_language_is_english = confirm(
            "Use English for STT language? (select No for Multi-Lingual)",
            default=(env.get("sttLanguage", "en") == "en"),
        )
        stt_language = "en" if stt_language_is_english else "multi"
        stt_prompt = prompt(
            "Enter new STT keywords (comma-separated)",
            default=env.get("sttPrompt", ""),
            validation=None,
        )
        deploy_prompt = env.get("functionId", "") or "N/A"
        deploy = confirm(
            f"Deploy function to environment (Current: '{deploy_prompt}')?",
            default=False,
        )
        if deploy:
            while True:
                func = prompt("Function (name or ID)")
                func_data = get_function(session, agent["id"], func)
                if func_data:
                    func = func_data.get("id", "")
                    break
        else:
            func = ""
        updated_data = {
            "name": env_name,
            "agentId": agent["id"],
            "functionId": func,
            "phoneNumber": phone,
            "recordingEnabled": recording,
            "redactionEnabled": redaction,
            "sttLanguage": stt_language,
            "sttPrompt": stt_prompt,
            "updatedAt": datetime.now().isoformat(),
        }
        response = session.patch(
            f"{API_BASE_URL}/v1/agents/{agent['id']}/environments/{env['id']}",
            json=updated_data,
        )
        response.raise_for_status()
        print_info(f"Updating environment variables...")
        manage_variables(session, agent["id"], env["id"], True)
        print_success(f"Environment '{env_name}' updated successfully")
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("delete")
def agent_env_delete(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID."),
    env_name_or_id: str = typer.Argument(..., help="Environment name or ID."),
):
    """Delete an environment. Provide agent name or ID and environment name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        env = get_environment(session, agent["id"], env_name_or_id)
        if not env:
            return
        if confirm(f"Are you sure you want to delete environment '{env['name']}'?"):
            response = session.delete(
                f"{API_BASE_URL}/v1/agents/{agent['id']}/environments/{env['id']}"
            )
            response.raise_for_status()
            print_success(f"Environment '{env['name']}' deleted successfully.")
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("deploy")
def agent_env_deploy(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID"),
    env_name_or_id: str = typer.Argument(..., help="Environment name or ID"),
    func_name_or_id: str = typer.Option(
        None, "--func", help="Function name or ID"
    ),
):
    """Deploy a function to an environment. Provide agent name or ID and environment name or ID. Optionally provide function name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        agent_id = agent.get("id")
        env = get_environment(session, agent["id"], env_name_or_id)
        if not env:
            return
        
        while True:
            func = func_name_or_id or prompt("Function (name or ID)")
            func_data = get_function(session, agent["id"], func)
            if func_data:
                func = func_data.get("id", "")
                break
            func_name_or_id = None
        
        data = {
            "agentId": agent_id,
            "functionId": func,
            "environmentId": env["id"]
        }
        
        if not confirm(
            f"Deploy function '{func_data.get('name', '')}' "
            f"to environment '{env['name']}'?"
        ):
            return
            
        response = session.patch(
            f"{API_BASE_URL}/v1/agents/{agent_id}/environments/{env['id']}", 
            json=data
        )
        response.raise_for_status()
        print_success(
            f"Function '{func_data.get('name', '')}' deployed to "
            f"environment '{env['name']}' successfully"
        )
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("undeploy")
def agent_env_undeploy(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID"), 
    env_name_or_id: str = typer.Argument(..., help="Environment name or ID")
):
    """Remove a function from an environment. Provide agent name or ID and environment name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        agent_id = agent.get("id")
        env = get_environment(session, agent["id"], env_name_or_id)
        if not env:
            return
        
        current_func_id = env.get("functionId", "")
        if not current_func_id:
            print_warning(
                f"No function currently deployed to environment '{env['name']}'"
            )
            return
        
        data = {
            "agentId": agent_id,
            "functionId": "",
            "environmentId": env["id"]
        }
        
        if not confirm(f"Remove function from environment '{env['name']}'?"):
            return
            
        response = session.patch(
            f"{API_BASE_URL}/v1/agents/{agent_id}/environments/{env['id']}", 
            json=data
        )
        response.raise_for_status()
        print_success(
            f"Function removed from environment '{env['name']}' successfully"
        )
    except requests.HTTPError as e:
        handle_http_error(e)


@app.command("debug")
def agent_func_debug(
    agent_name_or_id: str = typer.Argument(..., help="Agent name or ID"), 
    environment_name_or_id: str = typer.Argument(..., help="Environment name or ID")
):
    """Debug a function. Provide agent name or ID and function name or ID."""
    try:
        session = get_authenticated_session()
        agent = get_agent(session, agent_name_or_id)
        if not agent:
            return
        environment = get_environment(session, agent['id'], environment_name_or_id)
        if not environment:
            return
        function_id = environment.get('functionId')
        if not function_id:
            print_warning(
                f"No function deployed to environment '{environment['name']}'"
            )
            return
        function = get_function(session, agent['id'], function_id)
        if not function:
            return
        print_info(
            f"Debugging function '{function['name']}' in environment '{environment['name']}'"
        )
        asyncio.run(run_debugger(agent, environment, function))
    except requests.HTTPError as e:
        handle_http_error(e)
