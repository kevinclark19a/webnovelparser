
from typing import List
from re import sub

from requests import get
from bs4.element import Tag

from webtoepub.epub.resources import XMLTemplates


class EpubImage:
    
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

class EpubChapter:
    
    def __init__(self, index: int, source: str, title: str, chapter_contents: Tag) -> None:
        
        self._filename = f"OEBPS/Text/{index:04}_{EpubChapter.__fix_title(title)}.xhtml"
        self._index = index
        self._source = source
        self._title = title

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

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def index(self) -> int:
        return self._index
    
    @property
    def id(self) -> str:
        return  f"xhtml{self._index:04}"

    @property
    def source(self) -> str:
        return self._source

    @property
    def title(self) -> str:
        return self._title

    @property
    def contents(self) -> str:
        return self._contents.prettify()

    def extract_images(self) -> List[EpubImage]:

        images = []
        
        for image_tag in self._contents.find_all('img'):

            response = get(image_tag['src'], stream=True)
            content_type = response.headers.get('content-type')
            
            ext = content_type.split('/')[1]
            filename = f'Images/{len(images):04}_{EpubChapter.__fix_title(self.title)}.{ext}'

            image_tag['src'] = f'../{filename}'

            
            image = EpubImage(f'{self._index:04}image_{len(images)}',
                filename, content_type, response.content)

            images.append(image)

        return images

    @staticmethod
    def __fix_title(title: str) -> str:
        elipsis = '...'
        max_len = 25

        title = sub(r'\s', "_", title) # replace spaces with underscores
        title = sub(r'\W+', "", title) # remove all non-alphanumeric

        split_length = int((max_len - len(elipsis)) / 2)
        if len(title) > max_len:
            title = title[:split_length] + elipsis + title[-split_length:]

        return title