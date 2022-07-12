
from requests import get
from bs4 import BeautifulSoup

from webnovelparser.epub.resources import NovelMetadata, NovelChapter


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
    def __extract_chapter_data(html_obj: BeautifulSoup):
        chapter_table = html_obj.find(id="chapters").find('tbody')

        chapter_data = []
        for tr in chapter_table.find_all('tr'):
            chapter_link_tag = tr.find('a', href=lambda _: True)

            title_text = chapter_link_tag.text.strip()
            href = chapter_link_tag['href']
            chapter_data.append( (title_text, href) )

        return chapter_data

    def __init__(self, source: str, html_text: str) -> None:
        html_obj = BeautifulSoup(html_text, 'html.parser')

        author = _RoyalRoadStoryPage.__extract_author(html_obj)
        title = _RoyalRoadStoryPage.__extract_title(html_obj)
        self.chapter_data = _RoyalRoadStoryPage.__extract_chapter_data(html_obj)

        self.metadata = NovelMetadata(source, title, author, len(self.chapter_data))

        self._cover_image_url = _RoyalRoadStoryPage.__extract_cover_image_url(html_obj)

    def fetch_cover_image(self) -> bytes: # TODO: Can this use NovelImage?
        response = get(self._cover_image_url, stream=True)
        if not response.ok:
            return None
        return response.content


class RoyalRoadWebNovel:
    __BASE_URL = 'https://www.royalroad.com'

    def __init__(self, story_id, name_override=None) -> None:
        self._story_page = RoyalRoadWebNovel.__fetch_story_page(story_id)
        self._name_override = name_override

    @property
    def metadata(self) -> NovelMetadata:
        if self._name_override not in ("", None):
            return self._story_page.metadata.with_value(title=self._name_override)
        return self._story_page.metadata

    def set_name_override(self, new_name) -> None:
        self._name_override = new_name

    def get_chapter(self, index: int) -> NovelChapter:

        try:
            title, href = self._story_page.chapter_data[index]
            return RoyalRoadWebNovel.__fetch_chapter(index, title, href)
        except IndexError:
            raise ValueError(f"Web novel doesn't have a chapter number {index}.")

    def peek_chapter_title(self, index) -> str:

        try:
            title, _ = self._story_page.chapter_data[index]
            return title
        except IndexError:
            raise ValueError(f"Web novel doesn't have a chapter number {index}.")

    def get_cover_image(self):
        return self._story_page.fetch_cover_image()

    @staticmethod
    def __fetch_story_page(story_id: int) -> _RoyalRoadStoryPage:
        response = get(f'{RoyalRoadWebNovel.__BASE_URL}/fiction/{story_id}')
        response.raise_for_status()
        return _RoyalRoadStoryPage(response.url, response.text)

    @staticmethod
    def __fetch_chapter(index: int, title: str, href: str) -> NovelChapter:
        response = get(f'{RoyalRoadWebNovel.__BASE_URL}{href}')
        response.raise_for_status()

        html_obj = BeautifulSoup(response.text, 'html.parser')
        contents = html_obj.find(class_="chapter-inner")
        
        return NovelChapter(index, response.url, title, contents)