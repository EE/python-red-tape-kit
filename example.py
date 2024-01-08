import datetime
import io

from red_tape_kit.doc_ast import Attachment, Document, InlineSequence, Section, Table, TableCellSpan, UnorderedList


doc = Document(
    language_code='en',
    title='The Title',
    subject='The Subject',
    author='The Author',
    creator='The Creator',
    creation_date=datetime.datetime(2020, 1, 1, 12, 33, 45, tzinfo=datetime.timezone.utc),
    creation_place='The Place',
    body=[],
)


doc.body.append(Section(
    title='The First Section',
    body=[
        'The first paragraph.',
        'The second paragraph.',
        InlineSequence([
            'We allow ',
            Attachment(
                content_io=io.BytesIO(b'**Markdown** is sure better than PDFs.\n'),
                basename='example.md',
                text='attachments',
            ),
            '. Nice, isn\'t it?',
        ]),
    ],
))


doc.body.append(Section(
    title='The Second Section',
    body=[
        Section(
            title='The Subsection',
            body=[
                'The first paragraph.',
                'The second paragraph.',
            ],
        ),
        'The second paragraph.',
    ],
))


doc.body.append(Section(
    title='A definition list',
    body=[
        'This is a definition list:',
        {
            'term 1': 'definition 1',
            'term 2': 'definition 2',
        }
    ]
))


doc.body.append(Section(
    title='A table',
    body=[
        'This is a table, but may be not that much pretty:',
        Table(
            head=[
                [
                    'n',
                    'addition', TableCellSpan.COLUMN, TableCellSpan.COLUMN,
                    'multiplication', TableCellSpan.COLUMN, TableCellSpan.COLUMN,
                ],
                [TableCellSpan.ROW, '0', '1', '2', '0', '1', '2'],
            ],
            body=[
                ['0', '0', '1', '2', '0', '0', TableCellSpan.COLUMN],
                ['1', '1', '2', '3', '0', '1', '2'],
                ['2', '2', '3', '4', TableCellSpan.ROW, '2', '4'],
            ],
        ),
    ],
))


doc.body.append(Section(
    title='A list',
    body=[
        'This is an unordered list, a long one:',
        UnorderedList(
            items=[
                [
                    'First list item',
                    'With a second paragraph inside! BTW Armour-piercing fin-stabilized discarding sabot '
                    '(APFSDS), long dart penetrator, or simply dart ammunition is a type of kinetic '
                    'energy penetrator ammunition used to attack modern vehicle armour.',
                ]
            ] + [f'Item {i}' for i in range(50)],
        )
    ]
))


doc = doc.normalized()


if __name__ == '__main__':
    from red_tape_kit.docx import DOCXRenderer
    from red_tape_kit.html import HTMLRenderer
    from red_tape_kit.pdf import FPDFRenderer
    with open('example.html', 'wb') as fp:
        HTMLRenderer(doc).render(fp, indent='\t')
    with open('example.pdf', 'wb') as fp:
        FPDFRenderer(doc).render(fp)
    with open('example.docx', 'wb') as fp:
        DOCXRenderer(doc).render(fp)
