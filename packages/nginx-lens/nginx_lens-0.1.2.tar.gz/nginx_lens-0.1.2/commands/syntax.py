import typer
from rich.console import Console
from rich.table import Table
import subprocess
import os
import re

app = typer.Typer()
console = Console()

ERROR_RE = re.compile(r'in (.+?):(\d+)')

@app.command()
def syntax(
    config_path: str = typer.Argument(..., help="Путь к nginx.conf"),
    nginx_path: str = typer.Option("nginx", help="Путь к бинарю nginx (по умолчанию 'nginx')")
):
    """
    Проверяет синтаксис nginx-конфига через nginx -t. В случае ошибки показывает место в виде таблицы.
    """
    cmd = [nginx_path, "-t", "-c", os.path.abspath(config_path)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            console.print("[green]Синтаксис nginx-конфига корректен[/green]")
        else:
            console.print("[red]Ошибка синтаксиса![/red]")
        console.print(result.stdout)
        console.print(result.stderr)
        # Парсим ошибку
        err = result.stderr or result.stdout
        m = ERROR_RE.search(err)
        if m:
            file, line = m.group(1), int(m.group(2))
            msg = err.strip().split('\n')[-1]
            # Читаем контекст
            context = []
            try:
                with open(file) as f:
                    lines = f.readlines()
                start = max(0, line-3)
                end = min(len(lines), line+2)
                for i in range(start, end):
                    mark = "->" if i+1 == line else "  "
                    context.append((str(i+1), mark, lines[i].rstrip()))
            except Exception:
                context = []
            table = Table(title="Ошибка синтаксиса", show_header=True, header_style="bold red")
            table.add_column("File")
            table.add_column("Line")
            table.add_column("Message")
            table.add_column("Context")
            for ln, mark, code in context:
                table.add_row(file, ln, msg if mark == "->" else "", f"{mark} {code}")
            console.print(table)
    except FileNotFoundError:
        console.print(f"[red]Не найден бинарь nginx: {nginx_path}[/red]") 