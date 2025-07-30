import argparse
import json
import os
import queue
from typing import Optional
import contextlib

from dotenv import dotenv_values

# Third-party CLI prettification libraries
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

# Progress bar helper (light import)
from fastworkflow.utils.startup_progress import StartupProgress

# NOTE: heavy fastworkflow imports moved into run_main to avoid start-up delay

# Instantiate a global console for consistent styling
console = Console()


def _build_artifact_table(artifacts: dict[str, str]) -> Table:
    """Return a rich.Table representation for artifact key-value pairs."""
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Name", style="cyan", overflow="fold")
    table.add_column("Value", style="white", overflow="fold")
    for name, value in artifacts.items():
        table.add_row(str(name), str(value))
    return table


def print_command_output(command_output):
    """Pretty-print workflow output using rich panels and tables."""
    for command_response in command_output.command_responses:
        workflow_id = fastworkflow.ChatSession.get_active_workflow_id()

        # Collect body elements for the panel content
        body_renderables = []

        if command_response.response:
            body_renderables.append(Text(command_response.response, style="green"))

        if command_response.artifacts:
            body_renderables.extend(
                (
                    Text("Artifacts", style="bold cyan"),
                    _build_artifact_table(command_response.artifacts),
                )
            )
        if command_response.next_actions:
            actions_table = Table(show_header=False, box=None)
            for act in command_response.next_actions:
                actions_table.add_row(Text(str(act), style="blue"))
            body_renderables.extend(
                (Text("Next Actions", style="bold blue"), actions_table)
            )
        if command_response.recommendations:
            rec_table = Table(show_header=False, box=None)
            for rec in command_response.recommendations:
                rec_table.add_row(Text(str(rec), style="magenta"))
            body_renderables.extend(
                (Text("Recommendations", style="bold magenta"), rec_table)
            )

        panel_title = f"[bold yellow]Workflow {workflow_id}[/bold yellow]"
        # Group all renderables together
        group = Group(*body_renderables)
        # Use the group in the panel
        panel = Panel.fit(group, title=panel_title, border_style="green")
        console.print(panel)


def run_main(args):
    """Main function to run the workflow."""
    if not os.path.isdir(args.workflow_path):
        console.print(f"[bold red]Error:[/bold red] The specified workflow path '{args.workflow_path}' is not a valid directory.")
        exit(1)

    env_vars = {
        **dotenv_values(args.env_file_path),
        **dotenv_values(args.passwords_file_path)
    }
    if not env_vars.get("SPEEDDICT_FOLDERNAME"):
        raise ValueError(f"Env file {args.env_file_path} is missing or path is incorrect")
    if not env_vars.get("LITELLM_API_KEY_SYNDATA_GEN"):
        raise ValueError(f"Password env file {args.passwords_file_path} is missing or path is incorrect")

    if args.startup_command and args.startup_action:
        raise ValueError("Cannot provide both startup_command and startup_action")

    # ------------------------------------------------------------------
    # Startup progress bar – must start *before* heavy imports -----------
    # ------------------------------------------------------------------
    StartupProgress.begin(total=3)  # initial coarse steps (will grow later)

    console.print(Panel(f"Running fastWorkflow: [bold]{args.workflow_path}[/bold]", title="[bold green]fastworkflow[/bold green]", border_style="green"))
    console.print("[bold green]Tip:[/bold green] Type 'exit' to quit the application.")

    # ---------------------------------
    # Heavy imports after progress bar
    # ---------------------------------
    global fastworkflow
    import fastworkflow  # noqa: F401 – heavy
    from fastworkflow.utils.logging import logger

    StartupProgress.advance("Imported fastworkflow modules")

    # Validate commands directory now that logger is available
    commands_dir = os.path.join(args.workflow_path, "_commands")
    if not os.path.isdir(commands_dir):
        logger.info(f"No _commands directory found at {args.workflow_path}, exiting...")
        StartupProgress.end()
        return

    fastworkflow.init(env_vars=env_vars)
    StartupProgress.advance("fastworkflow.init complete")

    startup_action: Optional[fastworkflow.Action] = None
    if args.startup_action:
        with open(args.startup_action, 'r') as file:
            startup_action_dict = json.load(file)
        startup_action = fastworkflow.Action(**startup_action_dict)

    context_dict = None
    if args.context_file_path:
        with open(args.context_file_path, 'r') as file:
            context_dict = json.load(file)

    chat_session = fastworkflow.ChatSession(
        args.workflow_path, 
        workflow_context=context_dict,
        startup_command=args.startup_command, 
        startup_action=startup_action, 
        keep_alive=args.keep_alive
    )

    StartupProgress.advance("ChatSession ready")
    StartupProgress.end()

    chat_session.start()
    with contextlib.suppress(queue.Empty):
        if command_output := chat_session.command_output_queue.get(
            timeout=1.0
        ):
            print_command_output(command_output)
    while not chat_session.workflow_is_complete or args.keep_alive:
        user_command = console.input("[bold yellow]User > [/bold yellow]")
        if user_command == "exit":
            break

        chat_session.user_message_queue.put(user_command)

        command_output = chat_session.command_output_queue.get()
        print_command_output(command_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Assistant for workflow processing")
    parser.add_argument("workflow_path", help="Path to the workflow folder")
    parser.add_argument("env_file_path", help="Path to the environment file")
    parser.add_argument("passwords_file_path", help="Path to the passwords file")
    parser.add_argument(
        "--context_file_path", help="Optional context file path", default=""
    )
    parser.add_argument(
        "--startup_command", help="Optional startup command", default=""
    )
    parser.add_argument(
        "--startup_action", help="Optional startup action", default=""
    )
    parser.add_argument(
        "--keep_alive", help="Optional keep_alive", default=True
    )
    args = parser.parse_args()
    run_main(args)
