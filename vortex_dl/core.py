import asyncio
import httpx
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List

class VortexCore:
    def __init__(self, url: str, parts: int = 8, output_dir: str = "."):
        self.url = url
        self.parts = parts
        self.output_dir = Path(output_dir)
        self.timeout = httpx.Timeout(10.0, connect=60.0, read=None)
        self.metadata = {}
        self.state = [] 

    def _get_state_path(self) -> Path:
        return self.output_dir / f"{self.metadata['name']}.vortex"

    async def get_metadata(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(follow_redirects=True, timeout=self.timeout) as client:
            resp = await client.head(self.url)
            size = int(resp.headers.get("Content-Length", 0))
            cd = resp.headers.get("Content-Disposition")
            name = cd.split("filename=")[1].strip('"') if cd and "filename=" in cd else self.url.split("/")[-1]
            name = name.split("?")[0] or "download_vortex"
            
            accept_ranges = resp.headers.get("Accept-Ranges") == "bytes"
            self.metadata = {"name": name, "size": size, "ranges": accept_ranges}
            
            state_path = self._get_state_path()
            if state_path.exists() and accept_ranges:
                with open(state_path, "r") as f:
                    self.state = json.load(f)
                    self.parts = len(self.state)
            else:
                self._prepare_new_state(size)
                
            return self.metadata

    def _prepare_new_state(self, size: int):
        chunk_size = size // self.parts
        for i in range(self.parts):
            start = i * chunk_size
            end = size - 1 if i == self.parts - 1 else (i + 1) * chunk_size - 1
            self.state.append({
                "id": i,
                "start": start,
                "end": end,
                "current": start, 
                "completed": False
            })

    async def download_part(self, client: httpx.AsyncClient, part_id: int, file_path: Path, callback):
        p = self.state[part_id]
        if p["completed"]:

            await callback(part_id, (p["current"] - p["start"]))
            return

        headers = {"Range": f"bytes={p['current']}-{p['end']}"}
        
        try:
            async with client.stream("GET", self.url, headers=headers) as resp:
                resp.raise_for_status()
                with open(file_path, "rb+") as f:
                    f.seek(p["current"])
                    async for chunk in resp.aiter_bytes():
                        f.write(chunk)
                        p["current"] += len(chunk)
                        await callback(part_id, len(chunk))
 
                        self._save_checkpoint()
                p["completed"] = True
                self._save_checkpoint()
        except Exception:
            pass

    def _save_checkpoint(self):
        with open(self._get_state_path(), "w") as f:
            json.dump(self.state, f)

    async def start(self, progress_callback) -> str:
        meta = self.metadata
        output_path = self.output_dir / meta['name']
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not output_path.exists():
            with open(output_path, "wb") as f:
                f.truncate(meta['size'])

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            tasks = [self.download_part(client, i, output_path, progress_callback) for i in range(self.parts)]
            await asyncio.gather(*tasks)

        if all(p["completed"] for p in self.state):
            self._get_state_path().unlink(missing_ok=True)
            
        return str(output_path)