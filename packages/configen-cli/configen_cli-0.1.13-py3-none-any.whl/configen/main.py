from importlib.metadata import version, PackageNotFoundError
from rich.console import Console
from rich.prompt import Prompt

import asyncio
import typer
import uuid
import sys

from configen import system, api, property, runner

app = typer.Typer(invoke_without_command=True)
console = Console()

try:
    __version__ = version("configen-cli")
except PackageNotFoundError:
    __version__ = "unknown"


def server_error(http_code, http_body):
    if http_code != 200:
        console.print(f"❌[bold red]Server error:[/bold red] [italic]{http_body}[/italic]")
        return True
    return False


async def run_repl():
    while True:
        valid, error = property.validate_config()
        if valid:
            break

        console.print("🛠️[bold green]Setting .env properties...[/bold green]")
        property.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        property.CONFIGEN_API_KEY = "Fzvxa2A2Fmc6YmA0F6JK1ToO4g7EsLk7eWupnDYNLJw"
        property.CONFIGEN_API_URL = "https://api.configen.ai"
        property.HOST_ID = str(uuid.uuid4())

        with property.ENV_FILE.open("w") as f:
            f.write(f"CONFIGEN_API_KEY={property.CONFIGEN_API_KEY}\n")
            f.write(f"CONFIGEN_API_URL={property.CONFIGEN_API_URL}\n")
            f.write(f"HOST_ID={property.HOST_ID}\n")

        console.print(f"✅Properties successfully saved to [bold]{property.ENV_FILE}[/bold].")

    if not system.has_internet():
        console.print("❌[bold red]No internet connection![/bold red] [dim]🔌 Please check your network and try again.[/dim]")
        return None

    http_code, http_body = await api.start_session(__version__)
    if server_error(http_code, http_body):
        return None

    session_id = http_body['session_id']
    prompt_max_attempts = int(http_body['prompt_max_attempts'])

    console.print("🚀Configen is a tool that configures your system using natural language. For example, type [bold]Install openjdk[/bold] and it will handle the rest.")
    console.print("ℹ️ Enter [bold]/help[/bold] to view commands. Use [bold]/new[/bold] to restart. Exit with [bold]/exit[/bold] or [bold]Ctrl+C[/bold].")
    console.print("_" * 50)

    while True:
        try:
            user_ask = Prompt.ask("configen").strip()
            if not user_ask:
                continue
            if user_ask == "/exit":
                console.print("👋Goodbye boss!")
                break
            elif user_ask == "/help":
                console.print("""
[bold cyan]Available commands:[/bold cyan]

  [bold]/help[/bold]  Show this help message  
  [bold]/new[/bold]   Restart the session  
  [bold]/exit[/bold]  Exit the CLI
""")
            elif user_ask == "/new":
                console.print("🔄Restarting Configen session...")
                return await run_repl()
            else:
                http_code, http_body = await api.add_conversation(session_id, user_ask, property.CLI_INPUT_USR_ASK)
                if server_error(http_code, http_body):
                    return None

                pma = prompt_max_attempts
                completed = False

                while not completed and pma > 0:
                    if "commands" in http_body:
                        for command in http_body["commands"]:
                            console.print(f"{command["description"]}")
                            console.print(f"▶️ [bold]Running:[/bold] [italic]{command["command"]}[/italic]")
                            code, stdout = runner.run(command["command"])
                            if code == 10:
                                console.print(f"[bold red]{stdout}[/bold red]")
                                return None
                            elif code == 1:
                                cli_input = f"When running the command {command["command"]}, the following error occurred: {stdout}"
                                http_code, http_body = await api.add_conversation(session_id, cli_input, property.CLI_INPUT_CMD_ERROR)
                                if server_error(http_code, http_body):
                                    return None
                                else:
                                    continue
                            elif command["output_required"]:
                                cli_input = f'You requested the output of "{command["command"]}". Here it is:\n{stdout}'
                                http_code, http_body = await api.add_conversation(session_id, cli_input, property.CLI_INPUT_CMD_OUTPUT)
                                if server_error(http_code, http_body):
                                    return None
                                else:
                                    continue
                    elif "question" in http_body:
                        console.print(f"❓[bold]Question:[/bold] {http_body["question"]}")
                        user_answer = Prompt.ask("answer").strip()
                        cli_input = f'You asked: "{http_body["question"]}", user has responded with: "{user_answer}".'
                        http_code, http_body = await api.add_conversation(session_id, cli_input, property.CLI_INPUT_USR_ANSWER)
                        if server_error(http_code, http_body):
                            return None
                        else:
                            continue
                    elif "completed" in http_body:
                        if http_body["completed"]:
                            console.print(f"✅[bold green]{http_body["message"]}[/bold green]")
                        else:
                            console.print(f"❌[bold red]{http_body["message"]}[/bold red]")
                        completed = True
                        break
                    pma -= 1

                if not completed and pma == 0:
                    console.print(f"🤷‍♂️[bold yellow]Tried {prompt_max_attempts} times but couldn’t complete the task. Try asking more specifically.[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n👋Goodbye boss!")
            break


@app.callback()
def cli(ctx: typer.Context, version_flag: bool = typer.Option(None, "--version", "-v", is_eager=True, help="Show the Configen CLI version and exit", ), ):
    if version_flag:
        console.print(f"Version: {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        asyncio.run(run_repl())


if __name__ == "__main__":
    if len(sys.argv) == 1:
        asyncio.run(run_repl())
    else:
        app()
