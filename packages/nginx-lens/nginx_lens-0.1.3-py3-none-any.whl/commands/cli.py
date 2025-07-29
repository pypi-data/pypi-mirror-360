import typer
from rich.console import Console
from commands.health import health
from commands.analyze import analyze
from commands.tree import tree
from commands.diff import diff
from commands.route import route
from commands.include import include_tree
from commands.graph import graph
from commands.logs import app as logs_app
from commands.syntax import app as syntax_app

app = typer.Typer(help="nginx-lens — анализ и диагностика конфигураций Nginx")
console = Console()

app.command()(health)
app.command()(analyze)
app.command()(tree)
app.command()(diff)
app.command()(route)
app.command()(include_tree)
app.command()(graph)
app.add_typer(logs_app, name="logs")
app.add_typer(syntax_app, name="syntax")

if __name__ == "__main__":
    app() 