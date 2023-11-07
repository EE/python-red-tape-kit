import xml.etree.ElementTree as ET
from base64 import b64encode

from .doc_ast import DefinitionList, Image, InlineSequence, Paragraph, Section, Sequence, Table, Text, UnorderedList


class HTMLRenderer:
    def __init__(self, document):
        self.document = document
        self.root = ET.Element('html', lang=self.document.language_code)
        self.add_head()
        self.add_body()

    def add_head(self):
        head = ET.SubElement(self.root, 'head')
        ET.SubElement(head, 'meta', charset='utf-8')
        ET.SubElement(head, 'title').text = self.document.title.plain_string
        ET.SubElement(head, 'meta', name='description', content=self.document.subject.plain_string)
        ET.SubElement(head, 'meta', name='author', content=self.document.author.plain_string)
        ET.SubElement(head, 'meta', name='generator', content=self.document.creator.plain_string)
        ET.SubElement(head, 'meta', name='created', content=self.document.creation_date.isoformat())
        ET.SubElement(head, 'meta', name='viewport', content='width=device-width, initial-scale=1')
        ET.SubElement(head, 'link', rel='stylesheet', href='https://edwardtufte.github.io/tufte-css/tufte.css')

    def add_body(self):
        body = ET.SubElement(self.root, 'body')
        article = ET.SubElement(body, 'article')
        self.add_cover(article)
        self.add_element(article, self.document.body, heading_level=2)

    def add_cover(self, body):
        self.add_inline_element(ET.SubElement(body, 'h1'), self.document.title)
        subtitle = ET.SubElement(body, 'p', class_='subtitle')
        self.add_inline_element(subtitle, self.document.subject)
        ET.SubElement(subtitle, 'br')
        self.add_inline_element(subtitle, self.document.author)
        ET.SubElement(subtitle, 'br')
        ET.SubElement(subtitle, 'span').text = self.document.creation_place_and_date

    def add_element(self, html_el, element, heading_level):
        if isinstance(element, Section):
            self.add_section(html_el, element, heading_level)
        elif isinstance(element, Paragraph):
            self.add_paragraph(html_el, element)
        elif isinstance(element, Table):
            self.add_table(html_el, element)
        elif isinstance(element, UnorderedList):
            self.add_unordered_list(html_el, element)
        elif isinstance(element, DefinitionList):
            self.add_definition_list(html_el, element)
        elif isinstance(element, Sequence):
            self.add_sequence(html_el, element, heading_level)
        elif isinstance(element, Image):
            self.add_image(html_el, element)
        else:
            raise ValueError(f'Unknown element type {type(element)}')

    def add_sequence(self, html_el, sequence, heading_level):
        for i, sub_element in enumerate(sequence.items):
            self.add_element(html_el, sub_element, heading_level)

    def add_section(self, html_el, section, heading_level):
        assert heading_level >= 2
        if heading_level == 2:
            html_el = ET.SubElement(html_el, 'section')
        heading = ET.SubElement(html_el, f'h{heading_level}')
        self.add_inline_element(heading, section.title)
        self.add_element(html_el, section.body, heading_level + 1)

    def add_paragraph(self, html_el, paragraph):
        p = ET.SubElement(html_el, 'p')
        self.add_inline_element(p, paragraph.text)

    def add_table(self, html_el, table_data):
        table = ET.SubElement(html_el, 'table')
        thead = ET.SubElement(table, 'thead')
        tr = ET.SubElement(thead, 'tr')
        for heading in table_data.headings:
            th = ET.SubElement(tr, 'th')
            self.add_inline_element(th, heading)
        tbody = ET.SubElement(table, 'tbody')
        for data_row in table_data.rows:
            tr = ET.SubElement(tbody, 'tr')
            for data_cell in data_row:
                td = ET.SubElement(tr, 'td')
                self.add_inline_element(td, data_cell)

    def add_unordered_list(self, html_el, unordered_list):
        ul = ET.SubElement(html_el, 'ul')
        for item in unordered_list.items:
            li = ET.SubElement(ul, 'li')
            self.add_element(li, item, heading_level=None)

    def add_definition_list(self, html_el, definition_list):
        dl = ET.SubElement(html_el, 'dl')
        for term, definition in definition_list.items.items():
            dt = ET.SubElement(dl, 'dt')
            self.add_inline_element(dt, term)
            dd = ET.SubElement(dl, 'dd')
            self.add_element(dd, definition, heading_level=None)

    def add_image(self, html_el, image):
        figure = ET.SubElement(html_el, 'figure')
        content_type = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
        }[image.image_format]
        b64_str = b64encode(image.image_io.read()).decode()
        img_src = f'data:{content_type};base64,{b64_str}'
        img = ET.SubElement(figure, 'img', src=img_src)
        img.set('alt', image.caption.plain_string)

    def add_inline_element(self, html_el, element):
        if isinstance(element, Text):
            ET.SubElement(html_el, 'span').text = element.text
        elif isinstance(element, InlineSequence):
            for sub_element in element.items:
                self.add_inline_element(html_el, sub_element)
        else:
            raise ValueError(f'Unknown inline element type {type(element)}')

    def render(self, f):
        ET.ElementTree(self.root).write(f, encoding='utf-8', method='html')
