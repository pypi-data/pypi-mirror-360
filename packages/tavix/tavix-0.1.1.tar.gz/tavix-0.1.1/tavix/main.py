import typer
from tavix.commands.generate import generate
from tavix.commands.explain import explain
from tavix.commands.fix import fix
from tavix.commands.explain_code import explain_code
from tavix.commands.ask import ask
from tavix.commands.setup import setup, status, set_key

app = typer.Typer(help="Tavix: Your AI-powered shell assistant.")

app.command()(generate)
app.command()(explain)
app.command()(fix)
app.command()(explain_code)
app.command()(ask)
app.command()(setup)
app.command()(status)
app.command()(set_key)

if __name__ == "__main__":
    app() 