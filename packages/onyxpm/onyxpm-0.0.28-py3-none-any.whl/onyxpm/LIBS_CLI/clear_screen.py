import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def clear_screen():
    os.system('cls')
    console = Console()
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="center")
    grid.add_column(justify="right")
    grid.add_row("Product version : 0.4",
                 "[b]ONYX[/b] : Project Life Cycle Management",
                 datetime.now().ctime().replace(":", "[blink]:[/]"),
                 )
    console.print(Panel(grid))

