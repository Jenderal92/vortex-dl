import asyncio
import time
import typer
import sys
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.table import Table

from .core import VortexCore, check_for_updates
from .ui import VortexUI

__version__ = "1.0.0"

app = typer.Typer(help="Vortex-DL: High-Performance Async Downloader")
console = Console()


async def run_vortex(url: str, parts: int, output: str):
    console.clear()
    new_v = await check_for_updates(__version__)
    if new_v:
        console.print(
            f"[bold yellow]🔔 Update Tersedia:[/] v{new_v} (Anda menggunakan v{__version__})"
        )
        console.print(
            "[dim]Jalankan 'pip install --upgrade vortex-dl' untuk memperbarui.[/]\n"
        )

    console.print(VortexUI.header())

    core = VortexCore(url, parts, output)

    with console.status("[bold yellow]Menghubungkan ke server...[/]"):
        try:
            meta = await core.get_metadata()
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            return

    info_table = Table.grid(padding=(0, 2))
    info_table.add_row("[cyan]File:[/]", meta["name"])
    info_table.add_row("[cyan]Size:[/]", f"{meta['size'] / 1e6:.2f} MB")
    console.print(info_table)
    console.print("")

    progress = VortexUI.create_progress()

    with Live(progress, refresh_per_second=10):
        total_task = progress.add_task("[white]Total Progress", total=meta["size"])

        part_tasks = []
        for i, p in enumerate(core.state):
            completed_in_part = p["current"] - p["start"]
            task = progress.add_task(
                f"  ↳ Part {i+1}",
                total=(p["end"] - p["start"] + 1),
                completed=completed_in_part,
            )
            part_tasks.append(task)
            progress.update(total_task, advance=completed_in_part)

        async def update_ui(p_id: int, chunk_len: int):
            progress.update(total_task, advance=chunk_len)
            progress.update(part_tasks[p_id], advance=chunk_len)

        start_t = time.time()
        try:
            file_path = await core.start(update_ui)
        except Exception as e:
            console.print(f"\n[bold red]Terhenti:[/] {e}")
            return

        duration = time.time() - start_t

    speed = (meta["size"] / 1e6) / duration if duration > 0 else 0
    console.print(f"\n[bold green]✔ Selesai dalam {duration:.2f} detik![/]")
    console.print(f"[yellow]Lokasi:[/] {file_path}")
    console.print(f"[yellow]Speed :[/] {speed:.2f} MB/s")


@app.command()
def download(
    url: str = typer.Argument(..., help="URL file"),
    parts: int = typer.Option(8, "--parts", "-p"),
    output: str = typer.Option(".", "--output", "-o"),
):
    try:
        asyncio.run(run_vortex(url, parts, output))
    except KeyboardInterrupt:
        console.print("\n[bold red]✖ Dibatalkan.[/]")
        sys.exit(1)


if __name__ == "__main__":
    app()
