from dataclasses import dataclass
from typing import BinaryIO, Dict, List, Union


DocumentElement = Union[
    'Section',
    'Sequence',
    'Paragraph',
    'Table',
    'UnorderedList',
    'DefinitionList',
    'Image',

    # sugar elements, removed during normalization
    str,  # str is treated as a Paragraph
    Dict[str, 'DocumentElement'],  # Dict[str, DocumentElement] is treated as a DefinitionList
    List['DocumentElement'],  # List[DocumentElement] is treated as a Sequence
]


@dataclass
class Document:
    language_code: str
    title: str
    subject: str
    author: str
    creator: str
    creation_date: str
    creation_place: str
    body: DocumentElement

    @property
    def creation_place_and_date(self) -> str:
        date_str = self.creation_date.strftime('%Y-%m-%d')
        return f'{self.creation_place}, {date_str}'

    def normalized(self) -> 'Document':
        return Document(
            language_code=self.language_code,
            title=self.title,
            subject=self.subject,
            author=self.author,
            creator=self.creator,
            creation_date=self.creation_date,
            creation_place=self.creation_place,
            body=_normalized(self.body),
        )


@dataclass
class Section:
    title: str
    body: DocumentElement

    def normalized(self) -> 'Section':
        return Section(
            title=self.title,
            body=_normalized(self.body),
        )


@dataclass
class Sequence:
    items: List[DocumentElement]

    def normalized(self) -> 'Sequence':
        return Sequence(
            items=[_normalized(item) for item in self.items],
        )


@dataclass
class Paragraph:
    text: str

    def normalized(self) -> 'Paragraph':
        return self


@dataclass
class Table:
    headings: List[str]
    rows: List[List[str]]

    def normalized(self) -> 'Table':
        return self


@dataclass
class UnorderedList:
    items: List[DocumentElement]

    def normalized(self) -> 'UnorderedList':
        return UnorderedList(
            items=[_normalized(item) for item in self.items],
        )


@dataclass
class DefinitionList:
    items: Dict[str, DocumentElement]

    def normalized(self) -> 'DefinitionList':
        return DefinitionList(
            items={key: _normalized(value) for key, value in self.items.items()},
        )


@dataclass
class Image:
    image_io: BinaryIO
    image_format: str
    caption: str

    def normalized(self) -> 'Image':
        return self


def _normalized(element: DocumentElement) -> DocumentElement:
    if isinstance(element, str):
        return Paragraph(text=element).normalized()
    elif isinstance(element, dict):
        return DefinitionList(items=element).normalized()
    elif isinstance(element, list):
        return Sequence(items=element).normalized()
    else:
        return element.normalized()
