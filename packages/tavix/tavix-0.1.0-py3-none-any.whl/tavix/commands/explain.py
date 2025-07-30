import typer
from tavix.core.llm import GeminiLLM
from tavix.core import prompts
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def explain(command: str = typer.Argument(..., help="Shell command to explain.")):
    """Explain a shell command line by line."""
    llm = GeminiLLM()
    prompt = prompts.EXPLAIN_COMMAND_PROMPT.format(command=command)
    result = llm.generate(prompt)
    console.print(Markdown(result)) 