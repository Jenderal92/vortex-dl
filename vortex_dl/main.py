import asyncio
import time
import typer
import os
from typing import Optional
from rich.console import Console
from rich.live import Live
from rich.table import Table

from .core import VortexCore, check_for_updates
from .ui import VortexUI

__version__ = "1.3.0"
app = typer.Typer(help="Vortex-DL: Professional Async Downloader")
console = Console()

async def run_vortex(url: str, parts: int, output: str, checksum: str = None, ua: str = None, cookie: str = None):
    new_v = await check_for_updates(__version__)
    if new_v:
        console.print(f"[bold yellow]  Update Tersedia:[/] v{new_v} (Anda v{__version__})")
        console.print("[dim]Jalankan 'pip install -U vortex-dl' untuk memperbarui.[/]\n")

    headers = {}
    if ua: headers["User-Agent"] = ua
    if cookie: headers["Cookie"] = cookie

    console.print(VortexUI.header())
    core = VortexCore(url, parts, output, headers=headers if headers else None)

    with console.status("[bold yellow]Connecting to server...[/]"):
        try:
            meta = await core.get_metadata()
        except Exception as e:
            console.print(f"[bold red]Error Connection:[/] {e}")
            return

    info_table = Table.grid(padding=(0, 2))
    info_table.add_row("[cyan]File Name :[/]", meta["name"])
    info_table.add_row("[cyan]File Size :[/]", f"{meta['size'] / 1e6:.2f} MB")
    info_table.add_row("[cyan]Threads   :[/]", f"{core.parts} parts")
    
    # Deteksi jika ini adalah resume download
    is_resuming = any(p["current"] > p["start"] for p in core.state)
    if is_resuming:
        info_table.add_row("[yellow]Status    :[/]", "Resuming previous session...")
    
    console.print(info_table)
    console.print("")

    progress = VortexUI.create_progress()
    with Live(progress, refresh_per_second=10):
        # Progress bar utama
        total_task = progress.add_task("[white]Overall Progress", total=meta["size"])
        
        # Progress bar per part
        part_tasks = []
        current_total_done = 0
        for i, p in enumerate(core.state):
            done = p["current"] - p["start"]
            current_total_done += done
            task = progress.add_task(f"    Part {i+1}", total=(p["end"]-p["start"]+1), completed=done)
            part_tasks.append(task)
        
        # Update progress awal jika resume
        progress.update(total_task, completed=current_total_done)

        async def update_ui(p_id, chunk_len):
            progress.update(total_task, advance=chunk_len)
            progress.update(part_tasks[p_id], advance=chunk_len)

        start_t = time.time()
        file_path = await core.start(update_ui)
        duration = time.time() - start_t

    # Statistik Akhir
    speed = (meta["size"] / 1e6) / duration if duration > 0 else 0
    console.print(f"\n[bold green] Download Selesai![/]")
    console.print(f"[bold white]Lokasi:[/] [yellow]{file_path}[/]")
    console.print(f"[bold white]Waktu :[/] {duration:.2f} detik")
    console.print(f"[bold white]Speed :[/] {speed:.2f} MB/s")
    
    # Fitur Verifikasi Checksum
    if checksum:
        with console.status("[bold cyan]Memverifikasi integritas file (SHA256)...[/]"):
            try:
                is_valid = core.verify_checksum(file_path, checksum)
                if is_valid:
                    console.print("[bold green]  [HASH MATCH] File aman dan utuh.[/]")
                else:
                    console.print("[bold red]  [HASH MISMATCH] File mungkin korup atau tidak valid![/]")
            except Exception as e:
                console.print(f"[bold red] Gagal verifikasi:[/] {e}")

@app.command()
def download(
    url: Optional[str] = typer.Argument(None, help="URL file yang ingin diunduh"),
    parts: int = typer.Option(8, "--parts", "-p", help="Jumlah part download simultan"),
    output: str = typer.Option(".", "--output", "-o", help="Folder tujuan penyimpanan"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Download batch dari daftar URL di file teks"),
    checksum: Optional[str] = typer.Option(None, "--sha256", help="Verifikasi SHA256 setelah download selesai"),
    ua: Optional[str] = typer.Option(None, "--ua", help="Custom User-Agent"),
    cookie: Optional[str] = typer.Option(None, "--cookie", "-c", help="Custom Cookie string"),
):
    """
    Vortex-DL: Download file dengan kecepatan cahaya menggunakan Python Async.
    """
    if file:
        if not os.path.exists(file):
            console.print(f"[bold red]Error:[/] File list [underline]{file}[/] tidak ditemukan.")
            return
        
        with open(file, "r") as f:
            links = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
        
        console.print(f"[bold cyan]Ditemukan {len(links)} link dalam file batch.[/]")
        for i, link in enumerate(links):
            console.print(f"\n[bold magenta]Mengunduh Antrean {i+1}/{len(links)}...[/]")
            asyncio.run(run_vortex(link, parts, output, checksum, ua, cookie))
    
    elif url:
        asyncio.run(run_vortex(url, parts, output, checksum, ua, cookie))
    
    else:
        console.print("[bold yellow]Petunjuk Penggunaan:[/]")
        console.print("  vortex-dl <URL>")
        console.print("  vortex-dl --file links.txt")
        console.print("\nGunakan [bold]--help[/] untuk melihat semua opsi.")

if __name__ == "__main__":
    app()