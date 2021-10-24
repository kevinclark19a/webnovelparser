
from zipfile import ZipFile
from os.path import relpath

from bs4 import BeautifulSoup
from bs4.element import Tag

from webtoepub.epub.templates import XMLTemplates
from webtoepub.epub.resources import NovelMetadata, NovelChapter

class _TableOfContents:

    def __init__(self, metadata: NovelMetadata) -> None:
        
        self._repr: BeautifulSoup = XMLTemplates.get_xml('toc_ncx')
        self._nav_list = []

        self.__set_metadata(metadata)

    def add_entry(self, entry_id: int, entry_name: str, entry_location: str) -> None:
        nav_point = self._repr.new_tag('navPoint', attrs={
            'id': f'body{entry_id:04}',
            'playOrder': entry_id
        })

        nav_point.append(self._repr.new_tag('navLabel'))
        nav_point.find('navLabel').append(self._repr.new_tag('text'))
        nav_point.find('navLabel').find('text').string = entry_name

        nav_point.append(self._repr.new_tag('content', attrs={
            'src': entry_location
        }))

        self._nav_list.append(nav_point)
    
    def finalize(self) -> None:
        self._nav_list.sort(key=lambda nav_point: nav_point['playOrder'])
        for nav_point in self._nav_list:
            self._repr.find('navMap').append(nav_point)

    def __set_metadata(self, metadata: NovelMetadata) -> None:
        title_text = self._repr.new_tag('text')
        title_text.string = metadata.title
        self._repr.find('ncx').find('docTitle').append(title_text)

        unique_id = self._repr.new_tag('meta', attrs={ 'name': 'dtb:uid', 'content': metadata.source })
        self._repr.find('head').append(unique_id)

        # Don't know what these are for, but they seem to be fine with these default values.

        depth = self._repr.new_tag('meta', attrs={ 'name': 'dtb:depth', 'content': '2' })
        self._repr.find('head').append(depth)

        total_page_count = self._repr.new_tag('meta', attrs={ 'name': 'dtb:totalPageCount', 'content': '0' })
        self._repr.find('head').append(total_page_count)

        max_page_number = self._repr.new_tag('meta', attrs={ 'name': 'dtb:maxPageNumber', 'content': '0' })
        self._repr.find('head').append(max_page_number)

    def __str__(self) -> str:
        return str(self._repr)

class _ContentOpf:
    
    def __init__(self, metadata: NovelMetadata) -> None:
        self._repr: BeautifulSoup = XMLTemplates.get_xml('content_opf')
        self._manifest = {}
        self._spine = {}

        self.__set_metadata(metadata)

    def add_manifest_item(self, idx, href: str, id: str, media_type: str, add_to_spine: bool=False) -> None:
        self._manifest[idx] = self._repr.new_tag('item', attrs={
            'href': href, 'id': id, 'media-type': media_type
        })

        if add_to_spine:
            self._spine[idx] = self._repr.new_tag('itemref', attrs={'idref':id})

    def add_metadata_item(self, name: str, attrs) -> None:
        self._repr.find('metadata').append(self._repr.new_tag(name, attrs=attrs))

    def finalize(self) -> None:
        def sort_and_add_entries(collection: dict, dest: Tag):
            indexed_entries = []
            for key, val in collection.items():
                if not isinstance(key, int):
                    # If it isn't indexed, the order doesn't
                    #  matter. Add it straight away.
                    dest.append(val)
                    continue
                indexed_entries.append((key, val))
            
            indexed_entries.sort(key=lambda entry: entry[0])
            for key, val in indexed_entries:
                dest.append(val)

        manifest = self._repr.find('manifest')
        spine = self._repr.find('spine')

        sort_and_add_entries(self._manifest, manifest)
        sort_and_add_entries(self._spine, spine)


    def __set_metadata(self, metadata: NovelMetadata) -> None:
        metadata_tag = self._repr.find('package').find('metadata')

        title = self._repr.new_tag('dc:title')
        title.string = metadata.title
        metadata_tag.append(title)

        author = self._repr.new_tag('dc:creator', attrs={
            'opf:file-as': metadata.author,
            'opf:role': 'aut'
        })
        author.string = metadata.author
        metadata_tag.append(author)

        language = self._repr.new_tag('dc:language')
        language.string = 'en' # default everything to english, for now.
        metadata_tag.append(language)

        source = self._repr.new_tag('dc:identifier', attrs={
            'id': 'BookId',
            'opf:scheme': 'URI'
        })
        source.string = metadata.source
        metadata_tag.append(source)

    def __str__(self) -> str:
        return str(self._repr)

class EpubFile:
    
    def __init__(self, metadata: NovelMetadata, filename: str) -> None:

        self._zipfile = ZipFile(filename, 'w')

        self._toc = _TableOfContents(metadata)
        self._content_opf = _ContentOpf(metadata)
        
        # Populate barebones template
        self._content_opf.add_manifest_item("toc", href="toc.ncx",
            id="ncx", media_type="application/x-dtbncx+xml")

        EpubFile.__add_common_files(self._zipfile)

    def __enter__(self):
        self._zipfile.__enter__()
        return self
    
    def __exit__(self, exception_type, exception_val, tb):
        self._toc.finalize()
        self._content_opf.finalize()

        self._zipfile.writestr('OEBPS/content.opf', str(self._content_opf))
        self._zipfile.writestr('OEBPS/toc.ncx', str(self._toc))
        self._zipfile.__exit__(exception_type,exception_val, tb)


    def add_chapter(self, chapter: NovelChapter) -> None:
        # Order matters here, extracting the images changes chapter.contents.
        for image in chapter.extract_images():
            self._zipfile.writestr(f'OEBPS/{image.path}', image.content)
            self._content_opf.add_manifest_item(image.id, href=image.path,
                id=image.id, media_type=image.content_type)
        
        self._zipfile.writestr(f'OEBPS/{chapter.path}', chapter.contents.prettify())
        
        self._content_opf.add_manifest_item(chapter.index, href=chapter.path,
            id=chapter.id, media_type='application/xhtml+xml', add_to_spine=True)
        self._toc.add_entry(chapter.index, chapter.title, chapter.path)

    def add_cover(self, img_content: bytes) -> None:
        if not img_content:
            return

        cover = XMLTemplates.get_xhtml('chapter')
        cover.find('head').append(cover.new_tag('title'))
        cover.find('body').append(cover.new_tag('div'))
        cover.find('body').find('div').append(cover.new_tag('img', attrs={
            'src': '../Images/Cover.jpg', 'alt': ''
        }))
        
        self._zipfile.writestr('OEBPS/Images/Cover.jpg', img_content)
        self._zipfile.writestr('OEBPS/Text/Cover.xhtml', str(cover))

        self._content_opf.add_metadata_item('meta', attrs={ 'content': 'cover-image', 'name': 'cover' })

        self._content_opf.add_manifest_item('cover-image', 'Images/Cover.jpg', 'cover-image', 'image/jpeg')
        self._content_opf.add_manifest_item('cover', 'Text/Cover.xhtml', 'cover', 'application/xhtml+xml', add_to_spine=True)



    @staticmethod
    def __add_common_files(zipfile: ZipFile) -> None:
        
        zipfile.writestr("mimetype", "application/epub+zip")

        container_xml = XMLTemplates.get_xml('container')
        zipfile.writestr("META-INF/container.xml", str(container_xml))