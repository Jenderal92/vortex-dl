from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import (
    Progress, 
    BarColumn, 
    TextColumn, 
    TransferSpeedColumn, 
    TimeRemainingColumn, 
    SpinnerColumn,
    DownloadColumn
)
from rich.style import Style

class VortexUI:   
    @staticmethod
    def header() -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row(
            "[bold italic #00ffff]🌀  VORTEX-DL[/bold italic #00ffff]\n"
            "[dim white]The Ultra-Fast Asynchronous Multi-part Downloader[/dim white]"
        )
        return Panel(
            grid,
            style="on #000033",
            border_style="#6200ee",
            padding=(1, 2),
        )

    @staticmethod
    def create_progress() -> Progress:
        return Progress(
            SpinnerColumn(spinner_name="dots12", style="bold cyan"),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(
                bar_width=None,
                complete_style=Style(color="#00ffff"), 
                finished_style=Style(color="#00ff00")
            ),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        )