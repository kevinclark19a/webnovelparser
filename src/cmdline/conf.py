
from json import load, dump
from json.decoder import JSONDecodeError
from io import StringIO, open
from typing import List

class StoryEntry:

    @property
    def id(self) -> int:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def last_read(self) -> int:
        return self._last_read

    def toJSON(self):
        return {
            'is_story_entry': True,
            'id': self.id,
            'title': self.title,
            'last_read': self.last_read,
        }
    
    def with_value(self, **kwargs: dict):

        id = kwargs.pop('id', self.id)
        title = kwargs.pop('title', self.title)
        last_read = kwargs.pop('last_read', self.last_read)

        if kwargs not in ({}, None):
            raise ValueError(f'StoryEntry does not have the following fields: {kwargs.keys()}')

        return StoryEntry(id, title, last_read)
    
    def __str__(self) -> str:
        return f'{self.title}<{self.id}>: last_read={self.last_read}'
    
    def __init__(self, id: int, title: str, last_read: int):
        self._id = id
        self._title = title
        self._last_read = last_read

class Config:
    
    def __init__(self, filepath):

        try:
            self._file = open(filepath, 'r+')
            self._repr = Config.__validate_json_contents(self._file)
            self._file.seek(0) # Reset for writing, later on.
        except FileNotFoundError:
            self._file = open(filepath, 'w')
            self._repr = Config.__build_new_config_repr()
        except (JSONDecodeError, ValueError):
            self._repr = Config.__build_new_config_repr()

    @property
    def stories(self) -> List[StoryEntry]:
        return self._repr['stories'][:]

    def add_story(self, story: StoryEntry) -> None:
        # Ensure uniqueness on id.
        entry = self.fetch_story(id=story.id)
        if entry in self._repr['stories']:
            self._repr['stories'].remove(entry)

        self._repr['stories'].append(story)

    def remove_story(self, **kwargs):
        entry = self.fetch_story(**kwargs)

        if entry in self._repr['stories']:
            self._repr['stories'].remove(entry)
    
    def fetch_story(self, **kwargs) -> StoryEntry:
        id = title = None

        if 'id' in kwargs:
            id = kwargs.pop('id')
        if 'title' in kwargs:
            title = kwargs.pop('title')

        if kwargs not in ({}, None):
            raise ValueError(f'StoryEntry does not have the following identifiable fields: {kwargs.keys()}')
        
        def story_matches(story_entry: StoryEntry):
            matches = False

            if isinstance(id, int):
                matches = id == story_entry.id
            
            if isinstance(title, str):
                matches = (title.casefold() == story_entry.title.casefold())

            return matches
        
        return next((s for s in self._repr['stories'] if story_matches(s)), None)

    def __enter__(self):
        self._file.__enter__()
        return self

    def __exit__(self, exception_type, exception_val, tb):
        dump(self._repr, self._file, default=lambda obj: obj.toJSON())
        self._file.truncate()
        self._file.__exit__(exception_type, exception_val, tb)

    
    @staticmethod
    def __validate_json_contents(fobj):
        def story_entry(d):
            if 'is_story_entry' not in d:
                return d
            
            id = d.get('id', None)
            title = d.get('title', None)
            last_read = d.get('last_read', None)

            return StoryEntry(id, title, last_read)

        jobj = load(fobj, object_hook=story_entry)

        if 'stories' not in jobj:
            jobj['stories'] = []

        return jobj
    
    @staticmethod
    def __build_new_config_repr():
        config_template = StringIO('{}')
        return Config.__validate_json_contents(config_template)