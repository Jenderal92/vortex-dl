from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn, SpinnerColumn, DownloadColumn
from typing import Dict, Any

class VortexUI:   
    def __init__(self):
        self.console = Console()

    def get_banner(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row("[bold italic #00ffff]🌀 VORTEX-DL[/bold italic #00ffff]\n[dim white]The Ultra-Fast Asynchronous Downloader[/dim white]")
        return Panel(grid, style="on #000033", border_style="#6200ee", padding=(1, 2))

    @staticmethod
    def create_progress() -> Progress:
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(gradient=("#0000ff", "#00ffff", "#00ff00")),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        )

    def show_metadata(self, meta: Dict[str, Any], parts: int):
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("[bold magenta]Target File[/]", f"[white]{meta['name']}[/]")
        table.add_row("[bold magenta]File Size  [/]", f"[green]{meta['size'] / (1024*1024):.2f} MB[/]")
        table.add_row("[bold magenta]Segments   [/]", f"[cyan]{parts} Parallel Streams[/]")
        self.console.print(Panel(table, title="[bold yellow]Download Info[/]", border_style="yellow", expand=False))

    def show_summary(self, meta: Dict[str, Any], duration: float, checksum: str, path: str):
        avg_speed = (meta['size'] / (1024 * 1024)) / duration if duration > 0 else 0
        summary = Table(title="\n🚀 [bold green]DOWNLOAD SUCCESSFUL[/]", title_style="bold green")
        summary.add_row("Destination", path)
        summary.add_row("Average Speed", f"{avg_speed:.2f} MB/s")
        summary.add_row("MD5 Checksum", f"[yellow]{checksum}[/]")
        self.console.print(summary)

    def error(self, message: str):
        self.console.print(Panel(f"[bold red]ERROR:[/bold red] {message}", border_style="red"))
