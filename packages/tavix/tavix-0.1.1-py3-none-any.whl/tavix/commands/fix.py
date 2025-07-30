import typer
from tavix.core.llm import GeminiLLM
from tavix.core import prompts
from rich.console import Console

console = Console()

def fix(command: str = typer.Argument(..., help="Possibly broken shell command to fix.")):
    """Fix a broken shell command and explain the fix."""
    llm = GeminiLLM()
    prompt = prompts.FIX_COMMAND_PROMPT.format(command=command)
    result = llm.generate(prompt)
    console.print(result) 