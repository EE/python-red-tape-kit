import datetime
import io

import factory
import pytest
from freezegun import freeze_time

from red_tape_kit.doc_ast import Document, InlineSequence, Paragraph, Sequence, Text
from red_tape_kit.docx import DOCXRenderer
from red_tape_kit.html import HTMLRenderer
from red_tape_kit.pdf import FPDFRenderer


@pytest.fixture(params=[
    DOCXRenderer,
    FPDFRenderer,
    HTMLRenderer,
])
def renderer_class(request):
    return request.param


@pytest.fixture
def render(renderer_class):
    def f(doc):
        renderer = renderer_class(doc)
        memfile = io.BytesIO()
        renderer.render(memfile)
        memfile.seek(0)
        return memfile.read()
    return f


class DocumentFactory(factory.Factory):
    class Meta:
        model = Document

    language_code = 'en'
    title = Text('Test Document')
    subject = Text('Test Subject')
    author = Text('Test Author')
    creator = Text('Test Creator')
    creation_date = datetime.datetime(2017, 1, 1, 0, 0, 0)
    creation_place = Text('Test Place')
    body = factory.LazyAttribute(lambda o: Sequence(items=[]))


def test_nested_sequence(render):
    a = Paragraph(text=Text('A'))
    b = Paragraph(text=Text('B'))
    c = Paragraph(text=Text('C'))
    doc_a = DocumentFactory(
        body=Sequence(items=[
            Sequence(items=[a, b]),
            c
        ]),
    )
    doc_b = DocumentFactory(
        body=Sequence(items=[
            a,
            Sequence(items=[b, c]),
        ]),
    )
    assert render(doc_a) == render(doc_b)


def test_single_element_sequence(render):
    a = Paragraph(text=Text('A'))
    doc_a = DocumentFactory(
        body=Sequence(items=[a]),
    )
    doc_b = DocumentFactory(
        body=a,
    )
    assert render(doc_a) == render(doc_b)


def test_empty_sequence(render):
    a = Paragraph(text=Text('A'))
    doc_a = DocumentFactory(
        body=Sequence(items=[
            Sequence(items=[]),
            a,
        ]),
    )
    doc_b = DocumentFactory(
        body=a,
    )
    assert render(doc_a) == render(doc_b)


def test_nested_inline_sequence(render):
    a = Text('A')
    b = Text('B')
    c = Text('C')
    doc_a = DocumentFactory(
        body=Paragraph(text=InlineSequence(items=[
            InlineSequence(items=[a, b]),
            c
        ])),
    )
    doc_b = DocumentFactory(
        body=Paragraph(text=InlineSequence(items=[
            a,
            InlineSequence(items=[b, c]),
        ])),
    )
    assert render(doc_a) == render(doc_b)


def test_single_element_inline_sequence(render):
    a = Text('A')
    doc_a = DocumentFactory(
        body=Paragraph(text=InlineSequence(items=[a])),
    )
    doc_b = DocumentFactory(
        body=Paragraph(text=a),
    )
    assert render(doc_a) == render(doc_b)


def test_empty_inline_sequence(render):
    a = Text('A')
    doc_a = DocumentFactory(
        body=Paragraph(text=InlineSequence(items=[
            InlineSequence(items=[]),
            a,
        ])),
    )
    doc_b = DocumentFactory(
        body=Paragraph(text=a),
    )
    assert render(doc_a) == render(doc_b)


def test_not_dependent_on_current_date(render):
    doc = DocumentFactory()
    with freeze_time('2017-01-01'):
        a = render(doc)
    with freeze_time('2017-01-02'):
        b = render(doc)
    assert a == b
