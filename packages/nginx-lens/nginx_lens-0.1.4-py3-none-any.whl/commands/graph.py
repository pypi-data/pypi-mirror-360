import typer
from rich.console import Console
from parser.nginx_parser import parse_nginx_config
from exporter.graph import tree_to_dot, tree_to_mermaid

app = typer.Typer()
console = Console()

def graph(
    config_path: str = typer.Argument(..., help="Путь к nginx.conf"),
    format: str = typer.Option("dot", help="Формат: dot или mermaid")
):
    """
    Генерирует схему маршрутизации nginx (dot/mermaid).

    Пример:
        nginx-lens graph /etc/nginx/nginx.conf --format dot
        nginx-lens graph /etc/nginx/nginx.conf --format mermaid
    """
    tree = parse_nginx_config(config_path)
    if format == "dot":
        console.print(tree_to_dot(tree.directives))
    elif format == "mermaid":
        console.print(tree_to_mermaid(tree.directives))
    else:
        console.print("[red]Неизвестный формат: выберите dot или mermaid[/red]") 