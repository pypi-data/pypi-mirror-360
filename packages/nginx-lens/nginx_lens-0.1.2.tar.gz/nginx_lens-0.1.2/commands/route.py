import typer
from rich.console import Console
from rich.panel import Panel
from analyzer.route import find_route
from parser.nginx_parser import parse_nginx_config

app = typer.Typer()
console = Console()

def route(
    config_path: str = typer.Argument(..., help="Путь к nginx.conf"),
    url: str = typer.Argument(..., help="URL для маршрутизации (например, http://host/path)")
):
    """
    Показывает, какой server/location обслуживает указанный URL.
    """
    tree = parse_nginx_config(config_path)
    res = find_route(tree, url)
    if not res:
        console.print(Panel(f"Не найден подходящий server для {url}", style="red"))
        return
    server = res['server']
    location = res['location']
    proxy_pass = res['proxy_pass']
    text = f"[bold]Server:[/bold] {server.get('arg','') or '[no arg]'}\n"
    if location:
        text += f"[bold]Location:[/bold] {location.get('arg','')}\n"
    if proxy_pass:
        text += f"[bold]proxy_pass:[/bold] {proxy_pass}\n"
    console.print(Panel(text, title="Route", style="green")) 