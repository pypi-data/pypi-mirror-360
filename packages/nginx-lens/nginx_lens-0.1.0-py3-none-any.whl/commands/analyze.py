import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from analyzer.conflicts import find_location_conflicts
from analyzer.duplicates import find_duplicate_directives
from analyzer.empty_blocks import find_empty_blocks
from parser.nginx_parser import parse_nginx_config
from analyzer.warnings import find_warnings
from analyzer.unused import find_unused_variables

app = typer.Typer()
console = Console()

def analyze(config_path: str = typer.Argument(..., help="Путь к nginx.conf")):
    """
    Анализирует конфигурацию Nginx на типовые проблемы.
    """
    tree = parse_nginx_config(config_path)
    conflicts = find_location_conflicts(tree)
    dups = find_duplicate_directives(tree)
    empties = find_empty_blocks(tree)
    warnings = find_warnings(tree)
    unused_vars = find_unused_variables(tree)

    root = Tree("[bold blue]Анализ конфигурации Nginx[/bold blue]")

    if conflicts:
        node = root.add("[red]Конфликты location-ов[/red]")
        for c in conflicts:
            node.add(f"[yellow]server[/yellow]: {c['server'].get('arg', '')} [magenta]location[/magenta]: [bold]{c['location1']}[/bold] ↔ [bold]{c['location2']}[/bold]")
    else:
        root.add("[green]Нет конфликтов location-ов[/green]")

    if dups:
        node = root.add("[red]Дублирующиеся директивы[/red]")
        for d in dups:
            node.add(f"[yellow]{d['directive']}[/yellow] ([italic]{d['args']}[/italic]) — {d['count']} раз в блоке [cyan]{d['block'].get('block', d['block'])}[/cyan]")
    else:
        root.add("[green]Нет дублирующихся директив[/green]")

    if empties:
        node = root.add("[red]Пустые блоки[/red]")
        for e in empties:
            node.add(f"[yellow]{e['block']}[/yellow] [italic]{e['arg'] or ''}[/italic]")
    else:
        root.add("[green]Нет пустых блоков[/green]")

    if warnings:
        node = root.add("[bold yellow]Потенциальные проблемы[/bold yellow]")
        for w in warnings:
            if w['type'] == 'proxy_pass_no_scheme':
                node.add(f"[yellow]proxy_pass[/yellow] без схемы: [italic]{w['value']}[/italic]")
            elif w['type'] == 'autoindex_on':
                node.add(f"[yellow]autoindex on[/yellow] в блоке [cyan]{w['context'].get('block','')}[/cyan]")
            elif w['type'] == 'if_block':
                node.add(f"[yellow]Директива if[/yellow] внутри блока [cyan]{w['context'].get('block','')}[/cyan]")
            elif w['type'] == 'server_tokens_on':
                node.add(f"[yellow]server_tokens on[/yellow] в блоке [cyan]{w['context'].get('block','')}[/cyan]")
    else:
        root.add("[green]Нет потенциальных проблем[/green]")

    if unused_vars:
        node = root.add("[bold magenta]Неиспользуемые переменные[/bold magenta]")
        for v in unused_vars:
            node.add(f"[magenta]{v['name']}[/magenta]")
    else:
        root.add("[green]Нет неиспользуемых переменных[/green]")

    console.print(root) 