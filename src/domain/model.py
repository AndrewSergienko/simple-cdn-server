from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    file_type: str
    origin_url: str
    name: str | None = None


@dataclass
class Server:
    name: str
    ip: str
    zone: str


@dataclass
class ReplicatedFileStatus:
    file_url: str
    origin_url: str
    server: Server
    duration: int
    time: datetime
