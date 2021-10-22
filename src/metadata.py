

class NovelMetadata:

    def __init__(self, source: str, title: str, author: str):
        self._source = source
        self._title = title
        self._author = author

    @property
    def source(self) -> str:
        return self._source
    
    @property
    def author(self) -> str:
        return self._author

    @property
    def title(self) -> str:
        return self._title
