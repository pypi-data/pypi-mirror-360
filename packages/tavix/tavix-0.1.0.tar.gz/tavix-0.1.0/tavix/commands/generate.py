import typer
from typing import Optional
from tavix.core.llm import GeminiLLM
from tavix.core import prompts
import pyperclip
from rich.console import Console

console = Console()

def generate(
    task: str = typer.Argument(..., help="Describe the task you want to accomplish."),
    lang: Optional[str] = typer.Option(None, "--lang", help="Programming language (e.g., bash, python, cpp, java)"),
    explain: bool = typer.Option(False, "--explain", help="Add explanation of the code or command."),
    save: Optional[str] = typer.Option(None, "--save", help="Save the result to a file."),
    copy: bool = typer.Option(False, "--copy", help="Copy the result to clipboard."),
):
    """Generate a shell command or code snippet from a natural language task."""
    llm = GeminiLLM()
    prompt = (prompts.GENERATE_COMMAND_EXPLAIN_PROMPT if explain else prompts.GENERATE_COMMAND_PROMPT).format(
        task=task, lang=lang or "bash"
    )
    result = llm.generate(prompt)
    # If explanation is included, print with rich
    if explain:
        console.print(result)
    else:
        typer.echo(result)
    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]Saved result to {save}[/green]")
    if copy:
        pyperclip.copy(result)
        console.print("[cyan]Copied result to clipboard![/cyan]") 