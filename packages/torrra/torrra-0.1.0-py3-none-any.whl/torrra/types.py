from dataclasses import dataclass


@dataclass
class Torrent:
    title: str
    link: str


@dataclass
class Magnet:
    title: str
    magnet_uri: str
