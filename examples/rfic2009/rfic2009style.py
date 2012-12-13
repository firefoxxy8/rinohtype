
from copy import copy

import xml.etree.ElementTree as ET
##from lxml import etree, objectify

import pyte.frontend
pyte.frontend.XML_FRONTEND = 'pyte.frontend.xml.elementtree'

from pyte.unit import inch, pt, cm
from pyte.font import TypeFace, TypeFamily
from pyte.font.type1 import Type1Font
from pyte.font.opentype import OpenTypeFont
from pyte.font.style import REGULAR, MEDIUM, BOLD, ITALIC
from pyte.paper import Paper, LETTER
from pyte.document import Document, Page, Orientation
from pyte.layout import Container, DownExpandingContainer, FootnoteContainer
from pyte.layout import Chain
from pyte.paragraph import ParagraphStyle, Paragraph, LEFT, RIGHT, CENTER, BOTH
from pyte.paragraph import TabStop
from pyte.number import CHARACTER_UC, ROMAN_UC, NUMBER
from pyte.text import SingleStyledText, MixedStyledText
from pyte.text import Bold, Emphasized, SmallCaps, Superscript, Subscript
from pyte.text import TextStyle, BOLD_ITALIC_STYLE
from pyte.text import Tab as PyteTab
from pyte.math import MathFonts, MathStyle, Equation, EquationStyle
from pyte.math import Math as PyteMath
from pyte.structure import Heading, List
from pyte.structure import HeadingStyle, ListStyle
from pyte.structure import Header, Footer, HeaderStyle, FooterStyle
from pyte.structure import TableOfContents, TableOfContentsStyle
from pyte.reference import Field, Reference, REFERENCE
from pyte.reference import Footnote as PyteFootnote
from pyte.bibliography import Bibliography, BibliographyFormatter
from pyte.flowable import Flowable, FlowableStyle
from pyte.float import Figure as PyteFigure, CaptionStyle, Float
from pyte.table import Tabular as PyteTabular, MIDDLE
from pyte.table import HTMLTabularData, CSVTabularData, TabularStyle, CellStyle
from pyte.draw import LineStyle, RED
from pyte.style import ParentStyle
from pyte.frontend.xml import CustomElement, NestedElement
from pyte.backend import pdf, psg

from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import Citation, CitationItem, Locator



# use Gyre Termes instead of (PDF Core) Times
use_gyre = True

# fonts
# ----------------------------------------------------------------------------
if use_gyre:
    #termes_roman = Type1Font("../fonts/qtmr", weight=REGULAR)
    termes_roman = OpenTypeFont("../fonts/texgyretermes-regular.otf",
                                weight=REGULAR)
    termes_italic = Type1Font("../fonts/qtmri", weight=REGULAR, slant=ITALIC)
    termes_bold = Type1Font("../fonts/qtmb", weight=BOLD)
    termes_bold_italic = Type1Font("../fonts/qtmbi", weight=BOLD, slant=ITALIC)

    termes = TypeFace("TeXGyreTermes", termes_roman, termes_bold,
                      termes_italic, termes_bold_italic)
    cursor_regular = Type1Font("../fonts/qcrr", weight=REGULAR)
    cursor = TypeFace("TeXGyreCursor", cursor_regular)

    ieeeFamily = TypeFamily(serif=termes, mono=cursor)

    schola_roman = Type1Font("../fonts/qcsr", weight=REGULAR)
    schola_italic = Type1Font("../fonts/qcsri", weight=REGULAR, slant=ITALIC)
    schola_bold = Type1Font("../fonts/qcsb", weight=BOLD)
    heros_roman = Type1Font("../fonts/qhvr", weight=REGULAR)
    chorus = Type1Font("../fonts/qzcmi", weight=MEDIUM)
    standard_symbols = Type1Font("../fonts/usyr", weight=REGULAR)
    cmex9 = Type1Font("../fonts/cmex9", weight=REGULAR)

    mathfonts = MathFonts(schola_roman, schola_italic, schola_bold,
                          heros_roman, cursor_regular, chorus, standard_symbols,
                          cmex9)
else:
    from pyte.fonts.adobe14 import pdf_family as ieeeFamily
    #from pyte.fonts.adobe35 import palatino, helvetica, courier
    #from pyte.fonts.adobe35 import newcenturyschlbk, bookman
    #ieeeFamily = TypeFamily(serif=palatino, sans=helvetica, mono=courier)
    from pyte.fonts.adobe35 import postscript_mathfonts as mathfonts


# paragraph styles
# ----------------------------------------------------------------------------
bodyStyle = ParagraphStyle('body',
                           typeface=ieeeFamily.serif,
                           font_weight=REGULAR,
                           font_size=10*pt,
                           line_spacing=12*pt,
                           indent_first=0.125*inch,
                           space_above=0*pt,
                           space_below=0*pt,
                           justify=BOTH)

#TextStyle.attributes['kerning'] = False
#TextStyle.attributes['ligatures'] = False

ParagraphStyle.attributes['typeface'] = bodyStyle.typeface
ParagraphStyle.attributes['hyphen_lang'] = 'en_US'
ParagraphStyle.attributes['hyphen_chars'] = 4

mathstyle = MathStyle('math', fonts=mathfonts)

equationstyle = EquationStyle('equation', base=bodyStyle,
                              math_style=mathstyle,
                              indent_first=0*pt,
                              space_above=6*pt,
                              space_below=6*pt,
                              justify=CENTER,
                              tab_stops=[TabStop(0.5, CENTER),
                                         TabStop(1.0, RIGHT)])

toc_base_style = ParagraphStyle('toc level 1', base=bodyStyle,
                                tab_stops=[TabStop(0.6*cm),
                                           TabStop(1.0, RIGHT, '. ')])
toc_levels = [ParagraphStyle('toc level 1', font_weight=BOLD,
                             base=toc_base_style),
              ParagraphStyle('toc level 2', indent_left=0.5*cm,
                             base=toc_base_style),
              ParagraphStyle('toc level 3', indent_left=1.0*cm,
                             base=toc_base_style)]
toc_style = TableOfContentsStyle('toc', base=bodyStyle)

bibliographyStyle = ParagraphStyle('bibliography', base=bodyStyle,
                                   font_size=9*pt,
                                   indent_first=0*pt,
                                   space_above=0*pt,
                                   space_below=0*pt,
                                   tab_stops=[TabStop(0.25*inch, LEFT)])

titleStyle = ParagraphStyle("title",
                            typeface=ieeeFamily.serif,
                            font_weight=REGULAR,
                            font_size=18*pt,
                            line_spacing=1.2,
                            space_above=6*pt,
                            space_below=6*pt,
                            justify=CENTER)

authorStyle = ParagraphStyle("author",
                             base=titleStyle,
                             font_size=12*pt,
                             line_spacing=1.2)

affiliationStyle = ParagraphStyle("affiliation",
                                  base=authorStyle,
                                  space_below=6*pt + 12*pt)

abstractStyle = ParagraphStyle("abstract",
                               typeface=ieeeFamily.serif,
                               font_weight=BOLD,
                               font_size=9*pt,
                               line_spacing=10*pt,
                               indent_first=0.125*inch,
                               space_above=0*pt,
                               space_below=0*pt,
                               justify=BOTH)

listStyle = ListStyle("list", base=bodyStyle,
                      space_above=5*pt,
                      space_below=5*pt,
                      indent_left=0*inch,
                      indent_first=0*inch,
                      ordered=True,
                      item_spacing=0*pt,
                      numbering_style=NUMBER,
                      numbering_separator=')')

hd1Style = HeadingStyle("heading",
                        typeface=ieeeFamily.serif,
                        font_weight=REGULAR,
                        font_size=10*pt,
                        small_caps=True,
                        justify=CENTER,
                        line_spacing=12*pt,
                        space_above=18*pt,
                        space_below=6*pt,
                        numbering_style=ROMAN_UC)

unnumbered_heading_style = HeadingStyle("unnumbered", base=hd1Style,
                                        numbering_style=None)

hd2Style = HeadingStyle("subheading", base=hd1Style,
                        font_slant=ITALIC,
                        font_size=10*pt,
                        small_caps=False,
                        justify=LEFT,
                        line_spacing=12*pt,
                        space_above=6*pt,
                        space_below=6*pt,
                        numbering_style=CHARACTER_UC)
#TODO: should only specify style once for each level!

heading_styles = [hd1Style, hd2Style]

header_style = HeaderStyle('header', base=bodyStyle,
                           indent_first=0 * pt,
                           font_size=9 * pt)

footer_style = FooterStyle('footer', base=header_style,
                           indent_first=0 * pt,
                           justify=CENTER)

figure_style = FlowableStyle('figure',
                             space_above=10 * pt,
                             space_below=12 * pt)

fig_caption_style = CaptionStyle('figure caption',
                                 typeface=ieeeFamily.serif,
                                 font_weight=REGULAR,
                                 font_size=9*pt,
                                 line_spacing=10*pt,
                                 indent_first=0*pt,
                                 space_above=20*pt,
                                 space_below=0*pt,
                                 justify=BOTH)

footnote_style = ParagraphStyle('footnote', base=bodyStyle,
                                font_size=9*pt,
                                line_spacing=10*pt)

red_line_style = LineStyle('tabular line', width=0.2*pt, color=RED)
thick_line_style = LineStyle('tabular line')
tabular_style = TabularStyle('tabular',
                             typeface=ieeeFamily.serif,
                             font_weight=REGULAR,
                             font_size=10*pt,
                             line_spacing=12*pt,
                             indent_first=0*pt,
                             space_above=0*pt,
                             space_below=0*pt,
                             justify=CENTER,
                             vertical_align=MIDDLE,
                             left_border=red_line_style,
                             right_border=red_line_style,
                             bottom_border=red_line_style,
                             top_border=red_line_style,
                             )
first_row_style = CellStyle('first row', font_weight=BOLD,
                            bottom_border=thick_line_style)
first_column_style = CellStyle('first column', font_slant=ITALIC,
                               right_border=thick_line_style)
numbers_style = CellStyle('numbers', typeface=ieeeFamily.mono)
tabular_style.set_cell_style(first_row_style, rows=0)
tabular_style.set_cell_style(first_column_style, cols=0)
tabular_style.set_cell_style(numbers_style, rows=slice(1,None),
                             cols=slice(1,None))

# custom paragraphs
# ----------------------------------------------------------------------------

class Abstract(Paragraph):
    def __init__(self, text):
        label = SingleStyledText("Abstract &mdash; ", BOLD_ITALIC_STYLE)
        return super().__init__(label + text, abstractStyle)


class IndexTerms(Paragraph):
    def __init__(self, terms):
        label = SingleStyledText("Index Terms &mdash; ", BOLD_ITALIC_STYLE)
        text = ", ".join(sorted(terms)) + "."
        text = text.capitalize()
        return super().__init__(label + text, abstractStyle)


# render methods
# ----------------------------------------------------------------------------

class Section(CustomElement):
    def parse(self, document, level=1):
        for element in self.getchildren():
            if type(element) == Section:
                section = element.process(document, level=level + 1)
                for flowable in section:
                    yield flowable
            else:
                if isinstance(element, Title):
                    flowable = element.process(document, level=level,
                                               id=self.get('id', None))
                else:
                    flowable = element.process(document)
                yield flowable


class Title(NestedElement):
    def parse(self, document, level=1, id=None):
        return Heading(document, self.process_content(document),
                       style=heading_styles[level - 1], level=level, id=id)


class P(NestedElement):
    def parse(self, document):
        return Paragraph(self.process_content(document), style=bodyStyle)


class B(NestedElement):
    def parse(self, document):
        return Bold(self.process_content(document))


class Em(NestedElement):
    def parse(self, document):
        return Emphasized(self.process_content(document))


class SC(NestedElement):
    def parse(self, document):
        return SmallCaps(self.process_content(document))


class Sup(NestedElement):
    def parse(self, document):
        return Superscript(self.process_content(document))


class Sub(NestedElement):
    def parse(self, document):
        return Subscript(self.process_content(document))


class Tab(CustomElement):
    def parse(self, document):
        return MixedStyledText([PyteTab()])


class OL(CustomElement):
    def parse(self, document):
        return List([li.process(document) for li in self.li], style=listStyle)


class LI(NestedElement):
    pass


class Math(CustomElement):
    def parse(self, document):
        return PyteMath(self.text, style=mathstyle)


class Eq(CustomElement):
    def parse(self, document, id=None):
        equation = Equation(self.text, style=equationstyle)
        id = self.get('id', None)
        if id:
            document.elements[id] = equation
        return MixedStyledText([equation])


class Cite(CustomElement):
    def parse(self, document):
        keys = map(lambda x: x.strip(), self.get('id').split(','))
        items = [CitationItem(key) for key in keys]
        citation = Citation(items)
        document.bibliography.register(citation)
        return CitationField(citation)


class Ref(CustomElement):
    def parse(self, document):
        return Reference(self.get('id'), self.get('type', REFERENCE))


class Footnote(NestedElement):
    def parse(self, document):
        par = Paragraph(self.process_content(document), style=footnote_style)
        return PyteFootnote(par)


class Acknowledgement(CustomElement):
    def parse(self, document):
        yield Heading(document, 'Acknowledgement',
                      style=unnumbered_heading_style, level=1)
        for element in self.getchildren():
            yield element.process(document)


class Figure(CustomElement):
    def parse(self, document):
        caption_text = self.caption.process(document)
        scale = float(self.get('scale'))
        figure = PyteFigure(document, self.get('path'), caption_text,
                            scale=scale, style=figure_style,
                            caption_style=fig_caption_style)
        return Float(figure)


class Caption(NestedElement):
    pass


class Tabular(CustomElement):
    def parse(self, document):
        data = HTMLTabularData(self)
        return PyteTabular(data, style=tabular_style)


class CSVTabular(CustomElement):
    def parse(self, document):
        data = CSVTabularData(self.get('path'))
        return PyteTabular(data, style=tabular_style)


# bibliography
# ----------------------------------------------------------------------------

from pyte import csl_formatter

class IEEEBibliography(Paragraph):
    def __init__(self, items):
        items = [Paragraph(item, style=ParentStyle) for item in items]
        for item in items:
            item.parent = self
        return super().__init__(items, style=bibliographyStyle)

csl_formatter.Bibliography = IEEEBibliography


class CitationField(Field):
    def __init__(self, citation):
        super().__init__()
        self.citation = citation

    def warn_unknown_reference_id(self, item):
        self.warn("Unknown reference ID '{}'".format(item.key))

    def field_spans(self):
        text = self.citation.bibliography.cite(self.citation,
                                               self.warn_unknown_reference_id)
        field_text = SingleStyledText(text)
        field_text.parent = self.parent
        return field_text.spans()


# pages and their layout
# ----------------------------------------------------------------------------

class RFICPage(Page):
    topmargin = bottommargin = 1.125 * inch
    leftmargin = rightmargin = 0.85 * inch
    column_spacing = 0.25 * inch

    def __init__(self, document, first=False):
        super().__init__(document, LETTER, Orientation.Portrait)

        body_width = self.width - (self.leftmargin + self.rightmargin)
        body_height = self.height - (self.topmargin + self.bottommargin)
        body = Container(self, self.leftmargin, self.topmargin,
                         body_width, body_height)

        column_width = (body.width - self.column_spacing) / 2.0
        column_top = 0 * pt
        if first:
            self.title_box = DownExpandingContainer(body)
            column_top = self.title_box.bottom

        self.float_space = DownExpandingContainer(body, top=column_top)
        column_top = self.float_space.bottom

        self.content = document.content

        self.footnote_space = FootnoteContainer(body, 0*pt, body_height)
        self._footnote_number = 0

        self.column1 = Container(body, 0*pt, column_top,
                                 width=column_width,
                                 bottom=self.footnote_space.top,
                                 chain=document.content)
        self.column2 = Container(body, column_width + self.column_spacing, column_top,
                                 width=column_width,
                                 bottom=self.footnote_space.top,
                                 chain=document.content)

        self.column1._footnote_space = self.footnote_space
        self.column2._footnote_space = self.footnote_space
        self.column1._float_space = self.float_space
        self.column2._float_space = self.float_space

        self.header = Container(self, self.leftmargin, self.topmargin / 2,
                                body_width, 12*pt)
        footer_vert_pos = self.topmargin + body_height + self.bottommargin /2
        self.footer = Container(self, self.leftmargin, footer_vert_pos,
                                body_width, 12*pt)
        header_text = Header(header_style)
        self.header.add_flowable(header_text)
        footer_text = Footer(footer_style)
        self.footer.add_flowable(footer_text)


# main document
# ----------------------------------------------------------------------------
class RFIC2009Paper(Document):
    rngschema = 'rfic.rng'
    namespace = 'http://www.mos6581.org/ns/rficpaper'

    def __init__(self, filename, bibliography_source):
        super().__init__(filename, namespace=self.namespace,
                         schema=self.rngschema, backend=pdf)
        bibliography_style = CitationStylesStyle('ieee.csl')
        self.bibliography = CitationStylesBibliography(bibliography_style,
                                                       bibliography_source,
                                                       csl_formatter)

        authors = [author.text for author in self.root.head.authors.author]
        if len(authors) > 1:
            self.author = ', '.join(authors[:-1]) + ', and ' + authors[-1]
        else:
            self.author = authors[0]
        self.title = self.root.head.title.text
        self.keywords = [term.text for term in self.root.head.indexterms.term]
        self.parse_input()
        self.bibliography.sort()

    def parse_input(self):
        self.title_par = Paragraph(self.title, titleStyle)
        self.author_par = Paragraph(self.author, authorStyle)
        self.affiliation_par = Paragraph(self.root.head.affiliation.text,
                                         affiliationStyle)
        toc = TableOfContents(style=toc_style, styles=toc_levels)

        self.content_flowables = [Abstract(self.root.head.abstract.text),
                                  IndexTerms(self.keywords),
                                  Heading(self, 'Table of Contents',
                                          style=unnumbered_heading_style,
                                          level=1),
                                  toc]

        for section in self.root.body.section:
            for flowable in section.parse(self):
                toc.register(flowable)
                self.content_flowables.append(flowable)
        try:
            for flowable in self.root.body.acknowledgement.parse(self):
                toc.register(flowable)
                self.content_flowables.append(flowable)
        except AttributeError:
            pass
        bib_heading = Heading(self, 'References',
                              style=unnumbered_heading_style, level=1)
        self.content_flowables.append(bib_heading)

    def setup(self):
        self.page_count = 1
        self.content = Chain(self)
        page = RFICPage(self, first=True)
        self.add_page(page, self.page_count)

        page.title_box.add_flowable(self.title_par)
        page.title_box.add_flowable(self.author_par)
        page.title_box.add_flowable(self.affiliation_par)

        for flowable in self.content_flowables:
            self.content.add_flowable(flowable)

        bib = self.bibliography.bibliography()
        self.content.add_flowable(bib)

    def add_to_chain(self, chain):
        page = RFICPage(self)
        self.page_count += 1
        self.add_page(page, self.page_count)
        return page.column1
