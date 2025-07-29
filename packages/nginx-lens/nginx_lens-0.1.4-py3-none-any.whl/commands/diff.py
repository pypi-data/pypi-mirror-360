import typer
from rich.console import Console
from rich.table import Table
from analyzer.diff import diff_trees
from parser.nginx_parser import parse_nginx_config

app = typer.Typer()
console = Console()

def diff(
    config1: str = typer.Argument(..., help="Первый nginx.conf"),
    config2: str = typer.Argument(..., help="Второй nginx.conf")
):
    """
    Сравнивает две конфигурации Nginx и выводит отличия side-by-side.

    Пример:
        nginx-lens diff /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
    """
    tree1 = parse_nginx_config(config1)
    tree2 = parse_nginx_config(config2)
    diffs = diff_trees(tree1, tree2)
    if not diffs:
        console.print("[green]Конфигурации идентичны[/green]")
        return
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Config 1", style="red")
    table.add_column("Config 2", style="green")
    for d in diffs:
        path = "/".join(d['path'])
        if d['type'] == 'added':
            table.add_row("", f"+ {path}")
        elif d['type'] == 'removed':
            table.add_row(f"- {path}", "")
        elif d['type'] == 'changed':
            v1 = str(d['value1'])
            v2 = str(d['value2'])
            table.add_row(f"! {path}\n{v1}", f"! {path}\n{v2}")
    console.print(table) 