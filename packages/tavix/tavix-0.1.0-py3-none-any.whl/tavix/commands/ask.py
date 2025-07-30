import typer
from tavix.core.llm import GeminiLLM
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def ask(question: str = typer.Argument(..., help="Your general question or topic to ask about.")):
    """Ask Tavix anything! Get explanations, answers, and insights on any topic."""
    llm = GeminiLLM()
    prompt = f"""
You are a helpful AI assistant. Please provide a clear, informative, and engaging answer to the following question or topic. 
Use markdown formatting for better readability and structure your response appropriately.

Question/Topic: {question}

Please provide a comprehensive answer with examples if relevant.
"""
    result = llm.generate(prompt)
    console.print(Markdown(result)) 