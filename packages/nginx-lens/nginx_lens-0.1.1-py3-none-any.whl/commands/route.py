import typer
from rich.console import Console
from rich.table import Table
from analyzer.route import find_route
from parser.nginx_parser import parse_nginx_config
from upstream_checker.checker import check_upstreams

app = typer.Typer()
console = Console()

def route(
    config_path: str = typer.Argument(..., help="Путь к nginx.conf"),
    url: str = typer.Argument(..., help="URL для маршрутизации (например, http://host/path)"),
    timeout: float = typer.Option(2.0, help="Таймаут проверки (сек)"),
    retries: int = typer.Option(1, help="Количество попыток")
):
    """
    Показывает, какой server/location обслуживает указанный URL и статус upstream-ов (таблица).
    """
    tree = parse_nginx_config(config_path)
    res = find_route(tree, url)
    if not res:
        console.print("[red]Не найден подходящий server для {url}[/red]")
        return
    server = res['server']
    location = res['location']
    proxy_pass = res['proxy_pass']
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("upstream_name")
    table.add_column("upstream_status")
    # Проверяем upstream если есть proxy_pass
    if proxy_pass:
        upstreams = tree.get_upstreams()
        for name, servers in upstreams.items():
            if name in proxy_pass:
                results = check_upstreams({name: servers}, timeout=timeout, retries=retries)
                for srv in results[name]:
                    status = "Healthy" if srv["healthy"] else "Unhealthy"
                    color = "green" if srv["healthy"] else "red"
                    table.add_row(srv["address"], f"[{color}]{status}[/{color}]")
    else:
        table.add_row("-", "-")
    console.print(table) 