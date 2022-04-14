
from typing import List

from bs4.element import Tag
from re import sub, compile
from requests import get

from webtoepub.epub.templates import XMLTemplates


def _fix_filename(title: str) -> str:
    elipsis = '...'
    max_len = 25

    title = sub(r'\s', "_", title) # replace spaces with underscores
    title = sub(r'\W+', "", title) # remove all non-alphanumeric

    split_length = int((max_len - len(elipsis)) / 2)
    if len(title) > max_len:
        title = title[:split_length] + elipsis + title[-split_length:]

    return title

class NovelImage:
    
    def __init__(self, id, path, content_type, content):
        self._id = id
        self._path = path
        self._content_type = content_type
        self._content = content
    
    @property
    def id(self) -> str:
        return self._id

    @property
    def path(self) -> str:
        return self._path

    @property
    def content_type(self) -> str:
        return self._content_type

    @property
    def content(self) -> bytes:
        return self._content

class NovelChapter:

    def __init__(self, index: int, source: str, title: str, chapter_contents: Tag) -> None:

        contents = XMLTemplates.get_xhtml('chapter')
        head = contents.find('html').find('head')
        body = contents.find('html').find('body')

        title_tag = contents.new_tag('title')
        title_tag.string = title
        head.append(title_tag)

        title_tag = contents.new_tag('h1')
        title_tag.string = title
        body.append(title_tag)
        
        body.append(chapter_contents)

        self._contents = contents
        self._index = index
        self._source = source
        self._title = title

    @property
    def index(self) -> int:
        return self._index

    @property
    def source(self) -> str:
        return self._source
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def contents(self) -> Tag:
        return self._contents

    @property
    def id(self) -> str:
        return  f'xhtml{self.index:04}'

    @property
    def path(self) -> str:
        return f'Text/{self.index:04}_{_fix_filename(self.title)}.xhtml'

    def extract_images(self) -> List[NovelImage]:

        images = []
        
        for image_tag in self.contents.find_all('img'):
            try:
                response = get(image_tag['src'], stream=True)
                response.raise_for_status()
            except Exception:
                print(f'Failed to fetch image for chapter#{self.index}, removing...')
                image_tag.decompose()
            else:
                content_type = response.headers.get('content-type')
                ext = content_type.split('/')[1]

                filename = f'Images/{len(images):04}_{_fix_filename(self.title)}.{ext}'
                image_tag['src'] = f'../{filename}'
                
                image = NovelImage(f'{self.index}image{len(images)}',
                    filename, content_type, response.content)

                images.append(image)

        return images

    @staticmethod    
    def __fix_chapter_contents(content: Tag) -> None:

        # First, pick a better width value for tables.
        for td in content.find_all(['table', 'td'], {'width': True}):
            # TODO: This is a placeholder value, find a better one?
            td['width'] = 400
        
        # Next, turn `align` attrs into style
        for tag in content.find_all(True, {'align': True}):
            text_align = f'text-align: {td["align"]}'

            del td['align']
            if not tag.has_attr('style'):
                tag['style'] = text_align
            
            elif 'text-align' not in tag['style']:
                tag['style'] += f'; {text_align}'



class NovelMetadata:

    def __init__(self, source: str, title: str, author: str, num_chapters: int):
        self._source = source
        self._title = title
        self._author = author
        self._num_chapters = num_chapters

    def with_value(self, **kwargs: dict):

        source = kwargs.pop('source', self.source)
        title = kwargs.pop('title', self.title)
        author = kwargs.pop('author', self.author)
        num_chapters = kwargs.pop('num_chapters', self.num_chapters)

        if kwargs not in ({}, None):
            raise ValueError(f'NovelMetadata does not have the following fields: {kwargs.keys()}')

        return NovelMetadata(source, title, author, num_chapters)

    @property
    def source(self) -> str:
        return self._source
    
    @property
    def author(self) -> str:
        return self._author

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def num_chapters(self) -> int:
        return self._num_chapters
