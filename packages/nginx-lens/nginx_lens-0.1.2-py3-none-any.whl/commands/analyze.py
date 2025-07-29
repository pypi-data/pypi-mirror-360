import typer
from rich.console import Console
from rich.table import Table
from analyzer.conflicts import find_location_conflicts, find_listen_servername_conflicts
from analyzer.duplicates import find_duplicate_directives
from analyzer.empty_blocks import find_empty_blocks
from analyzer.warnings import find_warnings
from analyzer.unused import find_unused_variables
from parser.nginx_parser import parse_nginx_config
from analyzer.rewrite import find_rewrite_issues
from analyzer.dead_locations import find_dead_locations

app = typer.Typer()
console = Console()

def analyze(config_path: str = typer.Argument(..., help="Путь к nginx.conf")):
    """
    Анализирует конфигурацию Nginx на типовые проблемы. Выводит таблицу issue_type/issue_description.
    """
    tree = parse_nginx_config(config_path)
    conflicts = find_location_conflicts(tree)
    dups = find_duplicate_directives(tree)
    empties = find_empty_blocks(tree)
    warnings = find_warnings(tree)
    unused_vars = find_unused_variables(tree)
    listen_conflicts = find_listen_servername_conflicts(tree)
    rewrite_issues = find_rewrite_issues(tree)
    dead_locations = find_dead_locations(tree)

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("issue_type")
    table.add_column("issue_description")

    for c in conflicts:
        table.add_row("location_conflict", f"server: {c['server'].get('arg', '')} location: {c['location1']} ↔ {c['location2']}")
    for d in dups:
        table.add_row("duplicate_directive", f"{d['directive']} ({d['args']}) — {d['count']} раз в блоке {d['block'].get('block', d['block'])}")
    for e in empties:
        table.add_row("empty_block", f"{e['block']} {e['arg'] or ''}")
    for w in warnings:
        if w['type'] == 'proxy_pass_no_scheme':
            table.add_row("proxy_pass_no_scheme", f"proxy_pass без схемы: {w['value']}")
        elif w['type'] == 'autoindex_on':
            table.add_row("autoindex_on", f"autoindex on в блоке {w['context'].get('block','')}")
        elif w['type'] == 'if_block':
            table.add_row("if_block", f"директива if внутри блока {w['context'].get('block','')}")
        elif w['type'] == 'server_tokens_on':
            table.add_row("server_tokens_on", f"server_tokens on в блоке {w['context'].get('block','')}")
    for v in unused_vars:
        table.add_row("unused_variable", v['name'])
    for c in listen_conflicts:
        table.add_row("listen_servername_conflict", f"server1: {c['server1'].get('arg','')} server2: {c['server2'].get('arg','')} listen: {','.join(c['listen'])} server_name: {','.join(c['server_name'])}")
    for r in rewrite_issues:
        table.add_row(r['type'], r['value'])
    for l in dead_locations:
        table.add_row("dead_location", f"server: {l['server'].get('arg','')} location: {l['location'].get('arg','')}")

    if table.row_count == 0:
        console.print("[green]Проблем не найдено[/green]")
    else:
        console.print(table) 