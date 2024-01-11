from logging import getLogger

from fpdf import FPDF, FontFace, TitleStyle, XPos, YPos
from fpdf.outline import OutlineSection
from fpdf.syntax import DestinationXYZ

from .ast import (
    Attachment, DefinitionList, Image, InlineSequence, Paragraph, Section, Sequence, Strong, Table, TableCellSpan,
    Text, UnorderedList,
)


logger = getLogger(__name__)


class FPDFRenderer(FPDF):
    DEFAULT_LINE_HEIGHT = 1.5  # relative to font size
    DEFAULT_FONT_FAMILY = 'helvetica'
    DEFAULT_FONT_SIZE = 10  # pt
    MARGIN_LEFT = 20  # mm
    MARGIN_RIGHT = 20  # mm
    MARGIN_TOP = 20  # mm
    MARGIN_BOTTOM = 20  # mm
    SEQUENCE_SPACE = 7  # mm
    UNORDERED_LIST_HSPACE = 7  # mm
    UNORDERED_LIST_BULLET = '-'
    UNORDERED_LIST_BULLET_SPACE = 5  # mm

    def __init__(self, document, **kwargs):
        super().__init__(**kwargs, unit='mm', format='A4')
        self.document = document
        self.add_fonts()
        self.set_meta()
        self.configure_margins()
        self.add_cover()
        self.configure_section_title_styles()
        self.add_body()

    def set_meta(self):
        self.set_lang(self.document.language_code)
        self.set_title(self.document.title.plain_string)
        self.set_subject(self.document.subject.plain_string)
        self.set_author(self.document.author.plain_string)
        self.set_creator(self.document.creator.plain_string)
        self.set_creation_date(self.document.creation_date)

    def configure_margins(self):
        self.set_left_margin(self.MARGIN_LEFT)
        self.set_right_margin(self.MARGIN_RIGHT)
        self.set_top_margin(self.MARGIN_TOP)
        self.set_auto_page_break(True, self.MARGIN_BOTTOM)

    def add_cover(self):
        self.add_page()
        self.set_y(140)
        self.set_x(60)
        self.set_font(self.DEFAULT_FONT_FAMILY, size=24)
        self.add_inline_element(self.document.title)
        self.ln(self.get_line_height())
        self.set_font(self.DEFAULT_FONT_FAMILY, size=12)
        self.set_x(60)
        self.add_inline_element(self.document.subject)
        self.ln(self.get_line_height())
        self.set_x(60)
        self.add_inline_element(self.document.author)
        self.ln(self.get_line_height())
        self.set_x(60)
        self.cell_nl(text=self.document.creation_place_and_date)

    def configure_section_title_styles(self):
        common_section_style_kwargs = dict(
            font_family=self.DEFAULT_FONT_FAMILY,
            b_margin=5,
        )
        self.set_section_title_styles(
            level0=TitleStyle(
                font_size_pt=18,
                t_margin=6,
                **common_section_style_kwargs,
            ),
            level1=TitleStyle(
                font_size_pt=14,
                t_margin=4,
                **common_section_style_kwargs,
            ),
            level2=TitleStyle(
                font_size_pt=10,
                t_margin=3,
                **common_section_style_kwargs,
            ),
        )

    def add_body(self):
        self.add_page()
        self.set_font(self.DEFAULT_FONT_FAMILY, size=self.DEFAULT_FONT_SIZE)
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
                self.ln(self.SEQUENCE_SPACE)
            ln_required = self.add_element(sub_element, level)
            if ln_required:
                anything_generated = True
        return anything_generated

    def add_section(self, section, level):
        section_style = self.section_title_styles[level]

        with (
            self.offset_rendering() as pdf,
            pdf._use_title_style(section_style),
        ):
            pdf.add_inline_element(section.title)
            pdf.ln(pdf.get_line_height())
        if pdf.page_break_triggered:
            self.add_page()

        dest = DestinationXYZ(self.page, top=self.h_pt - self.y * self.k)
        with (
            self._marked_sequence(title=section.title.plain_string) as struct_elem,
            self._use_title_style(section_style),
        ):
            self.add_inline_element(section.title)
            self.ln(self.get_line_height())
        self._outline.append(
            OutlineSection(section.title.plain_string, level, self.page, dest, struct_elem)
        )
        self.add_element(section.body, level + 1)
        return True

    def add_paragraph(self, paragraph):
        self.add_inline_element(paragraph.text)
        return True

    def add_table(self, table_data):
        with self.table(
            num_heading_rows=len(table_data.head.rows),
        ) as table:
            self.add_elementary_table(table, table_data.head)
            self.add_elementary_table(table, table_data.body)
        return True

    def add_elementary_table(self, pdf_table, elementary_table):
        for ri, row in enumerate(elementary_table.rows):
            pdf_row = pdf_table.row()
            for ci, cell in enumerate(row):
                if isinstance(cell, TableCellSpan):
                    pass
                else:
                    pdf_row.cell(
                        cell.plain_string,
                        colspan=elementary_table.get_column_span(ri, ci),
                        rowspan=elementary_table.get_row_span(ri, ci),
                    )

    def add_unordered_list(self, unordered_list):
        orig_left_margin = self.l_margin
        new_left_margin = orig_left_margin + self.UNORDERED_LIST_BULLET_SPACE
        self.set_left_margin(new_left_margin)
        for i, item in enumerate(unordered_list.items):
            if i > 0:
                self.ln(self.UNORDERED_LIST_HSPACE)
            with self.unbreakable() as self:
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
        elif isinstance(inline_element, Attachment):
            return self.add_attachment(inline_element)
        elif isinstance(inline_element, Strong):
            return self.add_strong(inline_element)
        else:
            raise ValueError(f'Unknown inline element type {inline_element}')

    def add_text(self, text):
        self.write_lh(text.text)
        return text.text != ''

    def add_inline_sequence(self, inline_sequence):
        anything_generated = False
        for sub_element in inline_sequence.items:
            anything_generated |= self.add_inline_element(sub_element)
        return anything_generated

    def add_attachment(self, attachment):
        self.add_inline_element(attachment.text)
        attachment.content_io.seek(0)
        b = attachment.content_io.read()
        # fpdf validates that the bytes are truthy
        # it seems like an error in this library
        # here we work around it
        b = TruthyBytes(b)
        self.file_attachment_annotation(
            file_path=None,
            bytes=b,
            basename=attachment.basename,
            x=self.get_x(),
            y=self.get_y(),
            w=self.font_size,
            h=self.font_size,
        )
        return True

    def add_strong(self, strong):
        with self.use_font_face(FontFace(emphasis="BOLD")):
            return self.add_inline_element(strong.text)

    def header(self):
        pass

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # page number
        self.set_font(self.DEFAULT_FONT_FAMILY, size=8)
        self.cell(0, 10, f"Strona {self.page_no()}/{{nb}}", align="C")

    def add_fonts(self):
        pass

    def cell_nl(self, *args, line_height=None, **kwargs):
        line_height = self.get_line_height(line_height)
        self.cell(
            *args,
            new_x=XPos.LEFT,
            new_y=YPos.NEXT,
            h=line_height,
            **kwargs,
        )

    def write_lh(self, text, line_height=None, **kwargs):
        line_height_abs = self.get_line_height(line_height)
        self.write(h=line_height_abs, text=text, **kwargs)

    def get_line_height(self, line_height=None):
        if line_height is None:
            line_height = self.DEFAULT_LINE_HEIGHT
        return self.font_size * line_height

    def render(self, f):
        return self.output(f)


class TruthyBytes(bytes):
    def __bool__(self):
        return True
