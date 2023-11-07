import datetime
from dataclasses import dataclass
from typing import BinaryIO, Dict, List


class DocumentElement:
    """
    Block element can be for example a section, a paragraph, a table, etc.

    We allow some sugar in AST. Rules for normalization:
    - str is treated as a Paragraph
    - Dict[str, DocumentElement] is treated as a DefinitionList
    - List[DocumentElement] is treated as a Sequence
    """

    def normalized(self) -> 'DocumentElement':
        return self


class InlineElement:
    """
    Inline element can be for example plain text, an emphasis, a link, etc.

    We allow some sugar in AST. Rules for normalization:
    - str is treated as a Text
    """

    def normalized(self) -> 'InlineElement':
        return self

    @property
    def plain_string(self) -> str:
        raise NotImplementedError


@dataclass
class Document:
    language_code: str
    title: InlineElement
    subject: InlineElement
    author: InlineElement
    creator: InlineElement
    creation_date: datetime.datetime
    creation_place: InlineElement
    body: DocumentElement

    @property
    def creation_place_and_date(self) -> str:
        date_str = self.creation_date.strftime('%Y-%m-%d')
        return f'{self.creation_place.plain_string}, {date_str}'

    def normalized(self) -> 'Document':
        return Document(
            language_code=self.language_code,
            title=normalized_inline(self.title),
            subject=normalized_inline(self.subject),
            author=normalized_inline(self.author),
            creator=normalized_inline(self.creator),
            creation_date=self.creation_date,
            creation_place=normalized_inline(self.creation_place),
            body=_normalized(self.body),
        )


@dataclass
class Section(DocumentElement):
    title: InlineElement
    body: DocumentElement

    def normalized(self) -> 'Section':
        return Section(
            title=normalized_inline(self.title),
            body=_normalized(self.body),
        )


@dataclass
class Sequence(DocumentElement):
    items: List[DocumentElement]

    def normalized(self) -> 'Sequence':
        return Sequence(
            items=[_normalized(item) for item in self.items],
        )


@dataclass
class Paragraph(DocumentElement):
    text: InlineElement

    def normalized(self) -> 'Paragraph':
        return Paragraph(
            text=normalized_inline(self.text),
        )


@dataclass
class Table(DocumentElement):
    headings: List[InlineElement]
    rows: List[List[InlineElement]]

    def normalized(self) -> 'Table':
        return Table(
            headings=[normalized_inline(heading) for heading in self.headings],
            rows=[[normalized_inline(cell) for cell in row] for row in self.rows],
        )


@dataclass
class UnorderedList(DocumentElement):
    items: List[DocumentElement]

    def normalized(self) -> 'UnorderedList':
        return UnorderedList(
            items=[_normalized(item) for item in self.items],
        )


@dataclass
class DefinitionList(DocumentElement):
    items: Dict[InlineElement, DocumentElement]

    def normalized(self) -> 'DefinitionList':
        return DefinitionList(
            items={
                normalized_inline(key): _normalized(value)
                for key, value in self.items.items()
            },
        )


@dataclass
class Image(DocumentElement):
    image_io: BinaryIO
    image_format: str
    caption: InlineElement

    def normalized(self) -> 'Image':
        return Image(
            image_io=self.image_io,
            image_format=self.image_format,
            caption=normalized_inline(self.caption),
        )


def _normalized(element: DocumentElement) -> DocumentElement:
    if isinstance(element, str):
        return Paragraph(text=element).normalized()
    elif isinstance(element, dict):
        return DefinitionList(items=element).normalized()
    elif isinstance(element, list):
        return Sequence(items=element).normalized()
    elif isinstance(element, InlineElement):
        return Paragraph(text=element).normalized()
    else:
        return element.normalized()


@dataclass(frozen=True)
class Text(InlineElement):
    text: str

    def normalized(self) -> 'Text':
        return self

    @property
    def plain_string(self) -> str:
        return self.text


@dataclass(frozen=True)
class InlineSequence(InlineElement):
    items: List[InlineElement]

    def normalized(self) -> 'InlineSequence':
        return InlineSequence(
            items=[normalized_inline(item) for item in self.items],
        )

    @property
    def plain_string(self) -> str:
        return ''.join(item.plain_string for item in self.items)


def normalized_inline(element: InlineElement) -> InlineElement:
    if isinstance(element, str):
        return Text(text=element).normalized()
    elif isinstance(element, list):
        return InlineSequence(items=element).normalized()
    else:
        return element.normalized()
