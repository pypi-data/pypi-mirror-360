import typer
from tavix.core.llm import GeminiLLM
from tavix.core import prompts
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def explain_code(code: str = typer.Argument(..., help="Code snippet to explain.")):
    """Explain a code snippet line by line."""
    llm = GeminiLLM()
    prompt = prompts.EXPLAIN_CODE_PROMPT.format(code=code)
    result = llm.generate(prompt)
    console.print(Markdown(result)) 