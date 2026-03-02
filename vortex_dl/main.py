import asyncio
import time
import typer
from rich.console import Console
from rich.live import Live
from rich.table import Table
from .core import VortexCore
from .ui import VortexUI

app = typer.Typer(help="Vortex-DL: High-Performance Async Downloader")
console = Console()

async def run_vortex(url: str, parts: int, output: str):
    console.clear()
    console.print(VortexUI.header())
    
    core = VortexCore(url, parts, output)
    
    with console.status("[bold yellow]Menghubungkan ke server dan mengecek status...[/]"):
        try:
            meta = await core.get_metadata()
        except Exception as e:
            console.print(f"[bold red]Error:[/] Gagal mengambil metadata. {e}")
            return

    is_resume = any(p["current"] > p["start"] for p in core.state)
    
    info_table = Table.grid(padding=(0, 2))
    info_table.add_row("[cyan]File:[/]", meta['name'])
    info_table.add_row("[cyan]Size:[/]", f"{meta['size'] / 1e6:.2f} MB")
    info_table.add_row("[cyan]Mode:[/]", "Multi-part (Resume)" if is_resume else "New Download")
    console.print(info_table)
    console.print("")

    progress = VortexUI.create_progress()
    
    with Live(progress, refresh_per_second=10):
        total_task = progress.add_task("[white]Total Progress", total=meta['size'])
        
        part_tasks = []
        for i, p in enumerate(core.state):
            completed_in_part = p["current"] - p["start"]
            task = progress.add_task(
                f"  ↳ Part {i+1}", 
                total=(p["end"] - p["start"] + 1),
                completed=completed_in_part
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
            console.print(f"\n[bold red]Download terhenti:[/] {e}")
            return
        end_t = time.time()

    duration = end_t - start_t
    speed = (meta['size'] / 1e6) / duration if duration > 0 else 0
    
    console.print("\n[bold green]✔ Download Selesai![/]")
    
    summary = Table(show_header=False, border_style="blue", box=None)
    summary.add_row("[yellow]Lokasi[/]", file_path)
    summary.add_row("[yellow]Kecepatan Rata-rata[/]", f"{speed:.2f} MB/s")
    
    with console.status("[italic]Memverifikasi Integritas File (MD5)...[/]"):
        checksum = core.get_checksum(file_path)
        summary.add_row("[yellow]MD5 Checksum[/]", checksum)
    
    console.print(summary)

@app.command()
def download(
    url: str = typer.Argument(..., help="URL file yang ingin diunduh"),
    parts: int = typer.Option(8, "--parts", "-p", help="Jumlah part paralel (1-32)"),
    output: str = typer.Option(".", "--output", "-o", help="Direktori penyimpanan")
):
    """
    🌀 Jalankan Vortex-DL untuk mengunduh file dengan kecepatan cahaya.
    """
    try:
        asyncio.run(run_vortex(url, parts, output))
    except KeyboardInterrupt:
        console.print("\n[bold red]✘ Download dipause oleh pengguna.[/] Status disimpan.")

if __name__ == "__main__":
    app()