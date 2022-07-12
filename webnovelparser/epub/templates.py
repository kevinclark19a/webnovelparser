
from bs4 import BeautifulSoup
from pkg_resources import resource_string

class XMLTemplates:

    __BASE_DIRECTORY = 'data/xml_templates'

    @staticmethod
    def get_xml(filename: str) -> BeautifulSoup:
        
        if not filename.endswith(".xml"):
            filename += ".xml"
        
        xmltext = resource_string("webtoepub.epub", f'{XMLTemplates.__BASE_DIRECTORY}/{filename}')
        return BeautifulSoup(xmltext, "xml")

    @staticmethod
    def get_xhtml(filename: str) -> BeautifulSoup:
        if not filename.endswith(".xhtml"):
            filename += ".xhtml"
        
        xmltext = resource_string("webtoepub.epub", f'{XMLTemplates.__BASE_DIRECTORY}/{filename}')
        return BeautifulSoup(xmltext, "html.parser")