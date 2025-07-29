import typer
from rich.console import Console
from rich.panel import Panel
from analyzer.route import find_route
from parser.nginx_parser import parse_nginx_config
import glob
import os

app = typer.Typer()
console = Console()

def route(
    config_path: str = typer.Argument(None, help="Путь к nginx.conf (если не указан — поиск по всем .conf в /etc/nginx)", show_default=False),
    url: str = typer.Argument(..., help="URL для маршрутизации (например, http://host/path)")
):
    """
    Показывает, какой server/location обслуживает указанный URL.

    Пример:
        nginx-lens route /etc/nginx/nginx.conf http://example.com/api/v1
        nginx-lens route http://example.com/api/v1
    """
    configs = []
    if config_path:
        configs = [config_path]
    else:
        configs = glob.glob("/etc/nginx/**/*.conf", recursive=True)
        if not configs:
            console.print(Panel("Не найдено ни одного .conf файла в /etc/nginx", style="red"))
            return
    for conf in configs:
        try:
            tree = parse_nginx_config(conf)
        except Exception as e:
            continue  # пропускаем битые/невалидные
        res = find_route(tree, url)
        if res:
            server = res['server']
            location = res['location']
            proxy_pass = res['proxy_pass']
            text = f"[bold]Config:[/bold] {conf}\n"
            text += f"[bold]Server:[/bold] {server.get('arg','') or '[no arg]'}\n"
            if location:
                text += f"[bold]Location:[/bold] {location.get('arg','')}\n"
            if proxy_pass:
                text += f"[bold]proxy_pass:[/bold] {proxy_pass}\n"
            console.print(Panel(text, title="Route", style="green"))
            return
    console.print(Panel(f"Ни один ваш конфиг в /etc/nginx не обрабатывает этот URL", style="red")) 