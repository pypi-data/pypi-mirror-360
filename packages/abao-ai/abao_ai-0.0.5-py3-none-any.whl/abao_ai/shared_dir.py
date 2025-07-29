import os
import torch
from PIL import Image
from datetime import datetime
from einops import rearrange
from abao_ai.flux import Flux
from pathlib import Path
from abao_ai.info import get_devices
from filelock import FileLock


class SharedDir:
    def __init__(self, shared_dir: Path) -> None:
        self.shared_dir = shared_dir

    def lock(self) -> int:
        lock = FileLock(self.shared_dir / ".lock")
        with lock.acquire(timeout=5):
            seq_file = self.shared_dir / ".seq"
            with open(seq_file, "a") as f:
                f.write("")
            with open(seq_file, "r") as f:
                text = f.read()
                number = int(text if text else "0")
                number += 1
            with open(seq_file, "w") as f:
                f.write(str(number))
        return number

    def save_image(self, x: torch.Tensor) -> Path:
        x = x.clamp(-1, 1)
        x = rearrange(x[0], "c h w -> h w c")
        img = Image.fromarray((127.5 * (x + 1.0)).cpu().byte().numpy())

        number = self.lock()
        dir = self.shared_dir / "pngs" / str(number % 100)
        os.makedirs(dir, exist_ok=True)
        path = dir / f"{number}.png"
        img.save(path)
        return path
