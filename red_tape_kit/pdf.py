from logging import getLogger

from fpdf import FPDF, TitleStyle, XPos, YPos

from .doc_ast import DefinitionList, Image, InlineSequence, Paragraph, Section, Sequence, Table, Text, UnorderedList


logger = getLogger(__name__)


class FPDFRenderer(FPDF):
    default_font_family = 'helvetica'
    UNORDERED_LIST_BULLET = '-'

    def __init__(self, document, **kwargs):
        super().__init__(**kwargs, unit='mm', format='A4')
        self.document = document
        self.add_fonts()
        self.set_left_margin(20)
        self.set_right_margin(20)
        self.set_meta()
        self.add_cover()

        common_section_style_kwargs = dict(
            font_family=self.default_font_family,
            b_margin=5,
        )
        self.set_section_title_styles(
            level0=TitleStyle(
                font_size_pt=18,
                t_margin=20,
                **common_section_style_kwargs,
            ),
            level1=TitleStyle(
                font_size_pt=14,
                t_margin=15,
                **common_section_style_kwargs,
            ),
            level2=TitleStyle(
                font_size_pt=10,
                t_margin=10,
                **common_section_style_kwargs,
            ),
        )
        self.add_page()
        self.add_body()

    def set_meta(self):
        self.set_lang(self.document.language_code)
        self.set_title(self.document.title)
        self.set_subject(self.document.subject)
        self.set_author(self.document.author)
        self.set_creator(self.document.creator)
        self.set_creation_date(self.document.creation_date)

    def add_cover(self):
        self.add_page()
        self.set_y(140)
        self.set_x(60)
        self.set_font(self.default_font_family, size=24)
        self.cell_nl(text=self.document.title)
        self.set_font(self.default_font_family, size=12)
        self.cell_nl(text=self.document.subject)
        self.cell_nl(text=self.document.author)
        self.cell_nl(text=self.document.creation_place_and_date)

    def add_body(self):
        self.set_font(self.default_font_family, size=10)
        self.add_element(self.document.body, level=0)

    def add_element(self, element, level):
        """
        returns if anything was generated
        """
        if isinstance(element, Section):
            return self.add_section(element, level)
        elif isinstance(element, Paragraph):
            return self.add_paragraph(element)
        elif isinstance(element, Table):
            return self.add_table(element)
        elif isinstance(element, UnorderedList):
            return self.add_unordered_list(element)
        elif isinstance(element, DefinitionList):
            return self.add_definition_list(element)
        elif isinstance(element, Sequence):
            return self.add_sequence(element, level)
        elif isinstance(element, Image):
            return self.add_image(element)
        else:
            raise ValueError(f'Unknown element type {element}')

    def add_sequence(self, sequence, level):
        anything_generated = False
        ln_required = False
        for sub_element in sequence.items:
            if ln_required:
                self.ln(7)
            ln_required = self.add_element(sub_element, level)
            if ln_required:
                anything_generated = True
        return anything_generated

    def add_section(self, section, level):
        self.start_section(section.title.plain_string, level)
        return self.add_element(section.body, level + 1)

    def add_paragraph(self, paragraph):
        return self.add_inline_element(paragraph.text)

    def add_table(self, table_data):
        with self.table() as table:
            heading_row = table.row()
            for heading in table_data.headings:
                heading_row.cell(heading.plain_string)
            for data_row in table_data.rows:
                table_row = table.row()
                for data_cell in data_row:
                    table_row.cell(data_cell.plain_string)
        return True

    def add_unordered_list(self, unordered_list):
        orig_left_margin = self.l_margin
        new_left_margin = orig_left_margin + 5
        self.set_left_margin(new_left_margin)
        for i, item in enumerate(unordered_list.items):
            if i > 0:
                self.ln(7)
            with self.unbreakable():
                self.set_x(orig_left_margin)
                self.cell(text=self.UNORDERED_LIST_BULLET)
                self.set_x(new_left_margin)
                self.add_element(item, level=None)
        self.set_left_margin(orig_left_margin)
        return True

    def add_definition_list(self, definition_list):
        list_items = []
        for term, definition in definition_list.items.items():
            list_items.append(Sequence([
                Paragraph(term),
                definition,
            ]))
        self.add_element(UnorderedList(list_items), level=None)
        return True

    def add_image(self, image):
        self.image(image.image_io, w=100)
        return True

    def add_inline_element(self, inline_element):
        if isinstance(inline_element, Text):
            return self.add_text(inline_element)
        elif isinstance(inline_element, InlineSequence):
            return self.add_inline_sequence(inline_element)
        else:
            raise ValueError(f'Unknown inline element type {inline_element}')

    def add_text(self, text):
        self.write_lh(text.text)
        return text != ''

    def add_inline_sequence(self, inline_sequence):
        anything_generated = False
        for sub_element in inline_sequence.items:
            anything_generated |= self.add_inline_element(sub_element)
        return anything_generated

    def header(self):
        pass

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # page number
        self.set_font(self.default_font_family, size=8)
        self.cell(0, 10, f"Strona {self.page_no()}/{{nb}}", align="C")

    def add_fonts(self):
        pass

    def cell_nl(self, *args, **kwargs):
        line_height = self.font_size_pt / self.k
        self.cell(
            *args,
            new_x=XPos.LEFT,
            new_y=YPos.NEXT,
            h=line_height * 1.5,
            **kwargs,
        )

    def write_lh(self, text, line_height=1.5):
        line_height_abs = self.font_size_pt / self.k * line_height
        self.write(h=line_height_abs, text=text)

    def render(self, f):
        return self.output(f)
