import datetime
import io

from red_tape_kit.ast import (
    Attachment, Document, InlineSequence, Section, Strong, Table, TableCellSpan, Text, UnorderedList,
)


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
        Strong('Kava') + ' or ' + Strong('kava kava') + ' (Piper methysticum: Latin \'pepper\''
        ' and Latinized Greek \'intoxicating\') is a crop of the Pacific Islands.',
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
            Text('you can use ') + Strong('strong') + ' here': [
                'And here you can use block elmements.',
                'Like this paragraph.',
            ],
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
                    'number',
                    'addition', TableCellSpan.COLUMN, TableCellSpan.COLUMN,
                    'multiplication', TableCellSpan.COLUMN, TableCellSpan.COLUMN,
                ],
                [
                    TableCellSpan.ROW,
                    'of 0', 'of 1', 'of 2',
                    'by 0', 'by 1', 'by 2',
                ],
            ],
            body=[
                ['0', '0', '1', '2', '0', '0 (colspan)', TableCellSpan.COLUMN],
                ['1', 'who cares? (rowspan & colspan)', TableCellSpan.COLUMN, '3', '0 (rowspan)', '1', '2'],
                ['2', TableCellSpan.ROW, TableCellSpan.ROW, '4', TableCellSpan.ROW, '2', '4'],
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
