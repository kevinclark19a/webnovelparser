
from typing import Iterator

from requests import get
from bs4 import BeautifulSoup
from bs4.element import Tag

from webtoepub.metadata import NovelMetadata


class _RoyalRoadStoryPage:

    @staticmethod
    def __extract_author(html_obj: BeautifulSoup) -> str:
        raw_text: str = html_obj.find('h4', property="author").text.strip()
        if raw_text.startswith('by'):
            raw_text = raw_text[2:].strip()
        return raw_text

    @staticmethod
    def __extract_title(html_obj: BeautifulSoup) -> str:
        return html_obj.find('h1', property="name").text

    @staticmethod
    def __extract_cover_image_url(html_obj: BeautifulSoup) -> str:
        return html_obj.find(class_='cover-col').find('img')['src']

    @staticmethod
    def __extract_chapter_data(html_obj: BeautifulSoup) -> str:
        chapter_table = html_obj.find(id="chapters").find('tbody')

        return [
            (tr.find('td', href=lambda _: True).text.strip(), tr['data-url'] )
            for tr in chapter_table.find_all('tr')
        ]

    def __init__(self, source: str, html_text: str) -> None:
        html_obj = BeautifulSoup(html_text, 'html.parser')

        author = _RoyalRoadStoryPage.__extract_author(html_obj)
        title = _RoyalRoadStoryPage.__extract_title(html_obj)
        self.metadata = NovelMetadata(source, title, author)

        self._cover_image_url = _RoyalRoadStoryPage.__extract_cover_image_url(html_obj)
        self.chapter_data = _RoyalRoadStoryPage.__extract_chapter_data(html_obj)

    def fetch_cover_image(self) -> bytes:
        response = get(self._cover_image_url, stream=True)
        return response.content

class RoyalRoadChapter:

    @staticmethod
    def __extract_contents(html_obj: BeautifulSoup) -> Tag:
        return html_obj.find(class_="chapter-inner")
        
    
    def __init__(self, source: str, title: str, html_text: str) -> None:

        html_obj = BeautifulSoup(html_text, 'html.parser')
        self._contents = RoyalRoadChapter.__extract_contents(html_obj)

        self._source = source
        self._title = title

    @property
    def source(self) -> str:
        return self._source
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def contents(self) -> str:
        return self._contents

class RoyalRoadWebNovel:
    __BASE_URL = 'https://www.royalroad.com'

    def __init__(self, story_id) -> None:
        self._story_page = RoyalRoadWebNovel.__fetch_story_page(story_id)


    @property
    def metadata(self) -> NovelMetadata:
        return self._story_page.metadata

    def get_chapter(self, index: int) -> Iterator[RoyalRoadChapter]:

        try:
            title, url = self._story_page.chapter_data[index]
            return RoyalRoadWebNovel.__fetch_chapter(title, url)
        except IndexError:
            raise ValueError(f"Web novel doesn't have a chapter number {index}.")

    def get_cover_image(self):
        return self._story_page.fetch_cover_image()

    @staticmethod
    def __fetch_story_page(story_id: int) -> _RoyalRoadStoryPage:
        print(f'{RoyalRoadWebNovel.__BASE_URL}/fiction/{story_id}')
        response = get(f'{RoyalRoadWebNovel.__BASE_URL}/fiction/{story_id}')
        return _RoyalRoadStoryPage(response.url, response.text)

    @staticmethod
    def __fetch_chapter(title: str, url_stub: str) -> RoyalRoadChapter:
        response = get(f'{RoyalRoadWebNovel.__BASE_URL}{url_stub}')
        return RoyalRoadChapter(response.url, title, response.text)