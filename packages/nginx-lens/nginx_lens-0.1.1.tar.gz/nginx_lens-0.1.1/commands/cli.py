import typer
from rich.console import Console
from commands.health import health
from commands.analyze import analyze
from commands.tree import tree
from commands.diff import diff
from commands.route import route

app = typer.Typer(help="nginx-lens — анализ и диагностика конфигураций Nginx")
console = Console()

app.command()(health)
app.command()(analyze)
app.command()(tree)
app.command()(diff)
app.command()(route)

if __name__ == "__main__":
    app() 