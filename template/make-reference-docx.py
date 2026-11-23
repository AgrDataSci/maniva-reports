"""Build template/reference.docx, the styles of the Word version of a report, from a theme.

The Word version is for comments and edits. pandoc copies the styles of this file into
every Word report it writes, so headings, tables and captions follow the theme. Run it
again after a change to themes/<name>.yml. A build tool for a binary template, kept in
Python because it edits the XML inside the file. Needs pandoc and pyyaml.

Usage, from the repository root
    python3 template/make-reference-docx.py cgiar
"""
import io, os, re, subprocess, sys, zipfile
import yaml

theme = yaml.safe_load(open(os.path.join('themes', (sys.argv[1] if len(sys.argv) > 1 else 'cgiar') + '.yml'), encoding='utf-8'))
c = {k: v.lstrip('#').upper() for k, v in theme['colours'].items()}
font = theme['fonts'].get('docx', 'Arial')  # a font every reader of the Word file has

base = subprocess.run(['pandoc', '--print-default-data-file', 'reference.docx'], capture_output=True, check=True).stdout
zin = zipfile.ZipFile(io.BytesIO(base))
files = {n: zin.read(n) for n in zin.namelist()}
styles = files['word/styles.xml'].decode('utf-8')


def rpr(size, colour=None, bold=False, italic=False):
    return (f'<w:rPr><w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}" w:eastAsia="{font}"/>' +
            ('<w:b/><w:bCs/>' if bold else '') + ('<w:i/><w:iCs/>' if italic else '') +
            (f'<w:color w:val="{colour}"/>' if colour else '') + f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr>')


def para_style(sid, name, based, ppr, rp, extra=''):
    return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/><w:basedOn w:val="{based}"/>'
            f'<w:next w:val="BodyText"/><w:qFormat/>{extra}<w:pPr>{ppr}</w:pPr>{rp}</w:style>')


new = {
    'Title': para_style('Title', 'Title', 'Normal', '<w:keepNext/><w:spacing w:before="0" w:after="160"/>', rpr(52, c['primary'])),
    'Subtitle': para_style('Subtitle', 'Subtitle', 'Normal', '<w:keepNext/><w:spacing w:before="0" w:after="240"/>', rpr(28, c['primary_dark'])),
    'Author': para_style('Author', 'Author', 'Normal', '<w:spacing w:before="0" w:after="60"/>', rpr(22, c['ink'], bold=True)),
    'Date': para_style('Date', 'Date', 'Normal', '<w:spacing w:before="0" w:after="240"/>', rpr(20, c['muted'])),
    'Heading1': para_style('Heading1', 'heading 1', 'Normal',
                           '<w:keepNext/><w:keepLines/><w:pBdr><w:bottom w:val="single" w:sz="8" w:space="4" w:color="' + c['accent'] + '"/></w:pBdr>'
                           '<w:spacing w:before="360" w:after="200"/><w:outlineLvl w:val="0"/>', rpr(34, c['primary'], bold=True)),
    'Heading2': para_style('Heading2', 'heading 2', 'Normal', '<w:keepNext/><w:keepLines/><w:spacing w:before="280" w:after="100"/><w:outlineLvl w:val="1"/>',
                           rpr(26, c['primary'], bold=True)),
    'Heading3': para_style('Heading3', 'heading 3', 'Normal', '<w:keepNext/><w:keepLines/><w:spacing w:before="200" w:after="80"/><w:outlineLvl w:val="2"/>',
                           rpr(22, c['accent_dark'], bold=True)),
    'BodyText': para_style('BodyText', 'Body Text', 'Normal', '<w:spacing w:before="0" w:after="140" w:line="288" w:lineRule="auto"/>', rpr(20, c['ink'])),
    'FirstParagraph': para_style('FirstParagraph', 'First Paragraph', 'BodyText', '', ''),
    'Compact': para_style('Compact', 'Compact', 'BodyText', '<w:spacing w:before="20" w:after="20"/>', rpr(18, c['ink'])),
    'ImageCaption': para_style('ImageCaption', 'Image Caption', 'BodyText',
                               '<w:pBdr><w:left w:val="single" w:sz="18" w:space="6" w:color="' + c['accent'] + '"/></w:pBdr><w:spacing w:before="60" w:after="240"/>',
                               rpr(17, c['muted'], italic=True)),
    'CaptionedFigure': para_style('CaptionedFigure', 'Captioned Figure', 'BodyText', '<w:keepNext/><w:jc w:val="center"/>', ''),
    'Figure': para_style('Figure', 'Figure', 'BodyText', '<w:keepNext/><w:jc w:val="center"/>', ''),
}
for sid, xml in new.items():
    pat = re.compile(r'<w:style w:type="paragraph"[^>]*w:styleId="' + sid + r'".*?</w:style>', re.S)
    styles = pat.sub(lambda m: xml, styles, count=1) if pat.search(styles) else styles.replace('</w:styles>', xml + '</w:styles>')

# document defaults, the body font and size
styles = re.sub(r'<w:docDefaults>.*?</w:docDefaults>',
                f'<w:docDefaults><w:rPrDefault>{rpr(20, c["ink"])}</w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120"/></w:pPr></w:pPrDefault></w:docDefaults>',
                styles, count=1, flags=re.S)

# table style "Table" that pandoc applies, header row in the primary colour, light rules
table = (f'<w:style w:type="table" w:default="1" w:styleId="Table"><w:name w:val="Table"/><w:basedOn w:val="TableNormal"/><w:qFormat/>'
         f'<w:pPr><w:spacing w:before="20" w:after="20"/></w:pPr>{rpr(17, c["ink"])}'
         f'<w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:color="{c["rule"]}"/><w:bottom w:val="single" w:sz="4" w:color="{c["rule"]}"/>'
         f'<w:insideH w:val="single" w:sz="4" w:color="{c["rule"]}"/></w:tblBorders>'
         f'<w:tblCellMar><w:top w:w="40" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="40" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>'
         f'<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:color w:val="{c["primary_dark"]}"/></w:rPr>'
         f'<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{c["cover_subtext"]}"/></w:tcPr></w:tblStylePr>'
         f'<w:tblStylePr w:type="band2Horz"><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{c["tint"]}"/></w:tcPr></w:tblStylePr></w:style>')
pat = re.compile(r'<w:style w:type="table"[^>]*w:styleId="Table".*?</w:style>', re.S)
styles = pat.sub(lambda m: table, styles, count=1) if pat.search(styles) else styles.replace('</w:styles>', table + '</w:styles>')
# hyperlinks in the primary colour
styles = re.sub(r'(<w:style w:type="character"[^>]*w:styleId="Hyperlink".*?<w:color w:val=")[0-9A-Fa-f]{6}', r'\g<1>' + c['primary'], styles, count=1, flags=re.S)
files['word/styles.xml'] = styles.encode('utf-8')

# A4 page with the margins of the PDF
doc = files['word/document.xml'].decode('utf-8')
sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1191" w:right="1077" w:bottom="1134" w:left="1077" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr>')
doc = re.sub(r'<w:sectPr\s*/>|<w:sectPr>.*?</w:sectPr>', sect, doc, count=1, flags=re.S)
files['word/document.xml'] = doc.encode('utf-8')

out = os.path.join('template', 'reference.docx')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items():
        if not n.endswith('/'):
            z.writestr(n, b)
print(out)
