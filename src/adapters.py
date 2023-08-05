import os
import string
from datetime import datetime
from pathlib import Path
from random import choices

import aiofiles
from aiohttp import ClientSession

from src.abstract import adapters as abstract
from src.domain import File


class WebClient(abstract.AWebClient):
    async def download_file(self, link: str) -> File:
        async with ClientSession() as session:
            async with session.get(link) as resp:
                file_type = resp.content_type.split("/")[1]
                return File(file_type, await resp.read())


class FileManager(abstract.AFileManager):
    async def save_file(self, files_dir: Path, file: File) -> str:
        """
        Saving the file in the system.
        :param files_dir: dir of files
        :param file: bytes
        :return: file name
        """
        filename = file.name if file.name else self.generate_unique_filename()
        while os.path.exists(files_dir / filename):
            # If a file with that name already exists, generate a new one
            filename = self.generate_unique_filename()

        async with aiofiles.open(files_dir / f"{filename}.{file.file_type}", "wb") as f:
            await f.write(file.content)
            return f"{filename}.{file.file_type}"

    async def delete_file(self, files_dir: Path, file_name: str):
        pass

    def generate_unique_filename(self) -> str:
        """Getting a unique file name in the format <random_part>_<timestamp>."""
        basename = "".join(choices(string.ascii_letters + string.digits, k=5))
        suffix = int(datetime.now().timestamp())
        return f"{basename}_{suffix}"


class EnvManager(abstract.AEnvManager):
    async def get(self, key: str) -> str:
        return os.environ.get(key)