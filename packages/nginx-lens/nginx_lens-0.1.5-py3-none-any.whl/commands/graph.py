import typer
from rich.console import Console
from parser.nginx_parser import parse_nginx_config
from exporter.graph import tree_to_dot, tree_to_mermaid
from rich.text import Text

app = typer.Typer()
console = Console()

def graph(
    config_path: str = typer.Argument(..., help="Путь к nginx.conf")
):
    """
    Показывает все возможные маршруты nginx в виде цепочек server → location → proxy_pass → upstream → server.

    Пример:
        nginx-lens graph /etc/nginx/nginx.conf
    """
    tree = parse_nginx_config(config_path)
    routes = []
    # Для каждого server/location строим маршрут
    def walk(d, chain, upstreams):
        if d.get('block') == 'server':
            srv = d.get('arg','') or '[no arg]'
            for sub in d.get('directives', []):
                walk(sub, chain + [('server', srv)], upstreams)
        elif d.get('block') == 'location':
            loc = d.get('arg','')
            for sub in d.get('directives', []):
                walk(sub, chain + [('location', loc)], upstreams)
        elif d.get('directive') == 'proxy_pass':
            val = d.get('args','')
            # ищем, есть ли такой upstream
            up_name = None
            if val.startswith('http://') or val.startswith('https://'):
                up = val.split('://',1)[1].split('/',1)[0]
                if up in upstreams:
                    up_name = up
            if up_name:
                for srv in upstreams[up_name]:
                    routes.append(chain + [('proxy_pass', val), ('upstream', up_name), ('upstream_server', srv)])
            else:
                routes.append(chain + [('proxy_pass', val)])
        elif d.get('upstream'):
            # собираем upstream-ы
            upstreams[d['upstream']] = d.get('servers',[])
        # рекурсивно по всем директивам
        for sub in d.get('directives', []):
            walk(sub, chain, upstreams)
    # Собираем upstream-ы
    upstreams = {}
    for d in tree.directives:
        if d.get('upstream'):
            upstreams[d['upstream']] = d.get('servers',[])
    # Строим маршруты
    for d in tree.directives:
        walk(d, [], upstreams)
    if not routes:
        console.print("[yellow]Не найдено ни одного маршрута[/yellow]")
        return
    # Красивый вывод
    for route in routes:
        t = Text()
        for i, (typ, val) in enumerate(route):
            if typ == 'server':
                t.append(f"server: {val}", style="bold blue")
            elif typ == 'location':
                t.append(f" -> location: {val}", style="yellow")
            elif typ == 'proxy_pass':
                t.append(f" -> proxy_pass: {val}", style="green")
            elif typ == 'upstream':
                t.append(f" -> upstream: {val}", style="magenta")
            elif typ == 'upstream_server':
                t.append(f" -> server: {val}", style="grey50")
        console.print(t) 