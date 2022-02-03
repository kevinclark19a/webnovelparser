
from io import StringIO
from json import JSONDecodeError, load, dump
from typing import List, Type

from webtoepub.cmdline.config.bookshelf import Bookshelf, BookshelfConfigIdentifer
from webtoepub.cmdline.config.entry import StoryEntry
from webtoepub.cmdline.config.index import StoryIndex, StoryIndexConfigIdentifier
from webtoepub.cmdline.config.objects import ConfigObject, ConfigObjectIdentifier


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

    def stories(self, shelf_name: str=None) -> List[StoryEntry]:
        if shelf_name is None:
            return self._repr['index'].stories

        stories = []
        
        for bookshelf in self._repr['bookshelves']:
            if bookshelf.name == shelf_name:
                break

        for ref in bookshelf.get_references():
            if story := self._repr['index'].fetch_story(ref):
                stories.append(story)

        return stories

    @property
    def bookshelves(self) -> List[Bookshelf]:
        return self._repr['bookshelves'][:]

    def add_story(self, story: StoryEntry, shelves=None) -> None:

        # Just updating the entry
        if story in self._repr['index']:
            self._repr[story.coid] = story
            return

        # Not an exact match, ensure uniqueness on id.
        entry = self.fetch_story(id=story.id)
        if entry in self._repr['index']:
            self.remove_story(id=story.id)

        self._repr['index'].add_story(story)

    def remove_story(self, **kwargs):
        entry = self.fetch_story(**kwargs)

        for bookshelf in self._repr['bookshelves']:
            if entry.coid in bookshelf:
                bookshelf.remove_reference(entry)

        if entry in self._repr['index']:
            self._repr['index'].remove_story(entry)
    
    def fetch_story(self, **kwargs) -> StoryEntry:

        id = kwargs.pop('id', None)
        handle = kwargs.pop('handle', None)
        title = kwargs.pop('title', None)

        if kwargs not in ({}, None):
            raise ValueError(f'StoryEntry does not have the following identifiable fields: {kwargs.keys()}')
        
        def story_matches(story_entry: StoryEntry):
            matches = False

            if isinstance(id, int):
                matches = (id == story_entry.id)

            if isinstance(handle, str):
                matches = (handle.casefold() == story_entry.handle.casefold())
            
            if isinstance(title, str):
                matches = (title.casefold() == story_entry.title.casefold())

            return matches
        
        return next(filter(story_matches, self._repr['index'].stories), None)

    def create_bookshelf(self, name: str):
        
        if self.fetch_bookshelf(name) is None:    
            self._repr['bookshelves'].append(Bookshelf(name, []))
            return True

        return False
    
    def delete_bookshelf(self, name: str):
        
        if shelf := self.fetch_bookshelf(name):
            self._repr['bookshelves'].remove(shelf)
            return True
        
        return False
    
    def fetch_bookshelf(self, name: str) -> Bookshelf:
        try:
            return next(filter(lambda bs: bs.name == name, self._repr['bookshelves']))
        except StopIteration:
            return None


    def __enter__(self):
        self._file.__enter__()
        return self

    def __exit__(self, exception_type, exception_val, tb):
        dump(self._repr, self._file, default=lambda obj: obj.toJSON())
        self._file.truncate()
        self._file.__exit__(exception_type, exception_val, tb)

    
    @staticmethod
    def __validate_json_contents(fobj):

        def json_object_hook(data: dict) -> ConfigObject:

            top_level_coid_types: List[Type[ConfigObjectIdentifier]] = [
                StoryIndexConfigIdentifier,
                BookshelfConfigIdentifer
            ]

            coid_str = data.get("__coid", "")
            for coid_type in top_level_coid_types:
                if coid_type.matches(coid_str):
                    coid_inst = coid_type(coid_str)
                    return coid_inst.inflate_data(data)

            return data


        jobj: dict = load(fobj, object_hook=json_object_hook)

        if not isinstance(jobj.get('index', None), StoryIndex):
            jobj['index'] = StoryIndex()
        
        if 'bookshelves' not in jobj:
            jobj['bookshelves'] = []

        return jobj
    
    @staticmethod
    def __build_new_config_repr():
        config_template = StringIO('{}')
        return Config.__validate_json_contents(config_template)