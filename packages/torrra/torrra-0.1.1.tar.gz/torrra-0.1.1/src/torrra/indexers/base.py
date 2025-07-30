from typing import List
from selectolax.parser import HTMLParser

from torrra.types import Magnet, Torrent
from torrra.utils.html import parse_html
from abc import ABC, abstractmethod


class BaseIndexer(ABC):
    def _get_parser(self, url: str) -> HTMLParser:
        html = parse_html(url)
        return HTMLParser(html)

    @abstractmethod
    def search(self, query: str) -> List[Torrent]:
        pass

    @abstractmethod
    def get_magnets(self, link: str) -> List[Magnet]:
        pass
