import typer
from rich.console import Console
from rich.tree import Tree
from rich.text import Text
from analyzer.diff import diff_trees
from parser.nginx_parser import parse_nginx_config

app = typer.Typer()
console = Console()

def diff(
    config1: str = typer.Argument(..., help="Первый nginx.conf"),
    config2: str = typer.Argument(..., help="Второй nginx.conf")
):
    """
    Сравнивает две конфигурации Nginx и выводит отличия.
    """
    tree1 = parse_nginx_config(config1)
    tree2 = parse_nginx_config(config2)
    diffs = diff_trees(tree1, tree2)
    if not diffs:
        console.print("[green]Конфигурации идентичны[/green]")
        return
    root = Tree("[bold blue]Diff nginx.conf[/bold blue]")
    for d in diffs:
        path = "/".join(d['path'])
        if d['type'] == 'added':
            root.add(f"[green]+ {path}[/green]")
        elif d['type'] == 'removed':
            root.add(f"[red]- {path}[/red]")
        elif d['type'] == 'changed':
            node = root.add(f"[yellow]! {path}[/yellow]")
            node.add(f"[red]- {d['value1']}[/red]")
            node.add(f"[green]+ {d['value2']}[/green]")
    console.print(root) 