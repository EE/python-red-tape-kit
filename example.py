import datetime

from red_tape_kit.doc_ast import Document, Section, Table


doc = Document(
    language_code='en',
    title='The Title',
    subject='The Subject',
    author='The Author',
    creator='The Creator',
    creation_date=datetime.datetime(2020, 1, 1, 12, 33, 45),
    creation_place='The Place',
    body=[],
)


doc.body.append(Section(
    title='The First Section',
    body=[
        'The first paragraph.',
        'The second paragraph.',
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
            headings=['Heading 1', 'Heading 2'],
            rows=[
                ['A1', 'A2'],
                ['B1', 'B2'],
            ],
        ),
    ],
))


doc = doc.normalized()


if __name__ == '__main__':
    from red_tape_kit.docx import DOCXRenderer
    from red_tape_kit.html import HTMLRenderer
    from red_tape_kit.pdf import FPDFRenderer
    with open('example.html', 'wb') as fp:
        HTMLRenderer(doc).render(fp)
    with open('example.pdf', 'wb') as fp:
        FPDFRenderer(doc).render(fp)
    with open('example.docx', 'wb') as fp:
        DOCXRenderer(doc).render(fp)
