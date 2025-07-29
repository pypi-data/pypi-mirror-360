import typer
from rich.console import Console
from upstream_checker.checker import check_upstreams
from parser.nginx_parser import parse_nginx_config

app = typer.Typer()
console = Console()

def health(
    config_path: str = typer.Argument(..., help="Путь к nginx.conf"),
    timeout: float = typer.Option(2.0, help="Таймаут проверки (сек)"),
    retries: int = typer.Option(1, help="Количество попыток")
):
    """
    Проверяет доступность upstream-серверов, определённых в nginx.conf.
    """
    tree = parse_nginx_config(config_path)
    upstreams = tree.get_upstreams()
    results = check_upstreams(upstreams, timeout=timeout, retries=retries)
    for name, servers in results.items():
        console.print(f"[bold]{name}[/bold]")
        for srv in servers:
            status = "[green]Healthy ✅[/green]" if srv["healthy"] else "[red]Unhealthy ❌[/red]"
            console.print(f"  {srv['address']} {status}") 