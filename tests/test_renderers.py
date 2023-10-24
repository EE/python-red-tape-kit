import datetime
import io

import factory
import pytest
from freezegun import freeze_time

from red_tape_kit.doc_ast import Document, Paragraph, Sequence
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
    title = 'Test Document'
    subject = 'Test Subject'
    author = 'Test Author'
    creator = 'Test Creator'
    creation_date = datetime.datetime(2017, 1, 1, 0, 0, 0)
    creation_place = 'Test Place'
    body = factory.LazyAttribute(lambda o: Sequence(items=[]))


def test_nested_sequence(render):
    doc_a = DocumentFactory(
        body=Sequence(items=[
            Sequence(items=[
                Paragraph(text='A'),
                Paragraph(text='B'),
            ]),
            Paragraph(text='C'),
        ]),
    )
    doc_b = DocumentFactory(
        body=Sequence(items=[
            Paragraph(text='A'),
            Sequence(items=[
                Paragraph(text='B'),
                Paragraph(text='C'),
            ]),
        ]),
    )
    assert render(doc_a) == render(doc_b)


def test_single_element_sequence(render):
    doc_a = DocumentFactory(
        body=Sequence(items=[
            Paragraph(text='A'),
        ]),
    )
    doc_b = DocumentFactory(
        body=Paragraph(text='A'),
    )
    assert render(doc_a) == render(doc_b)


def test_empty_sequence(render):
    doc_a = DocumentFactory(
        body=Sequence(items=[
            Sequence(items=[]),
            Paragraph(text='A'),
        ]),
    )
    doc_b = DocumentFactory(
        body=Paragraph(text='A'),
    )
    assert render(doc_a) == render(doc_b)


def test_not_dependent_on_current_date(render):
    doc = DocumentFactory()
    with freeze_time('2017-01-01'):
        a = render(doc)
    with freeze_time('2017-01-02'):
        b = render(doc)
    assert a == b
