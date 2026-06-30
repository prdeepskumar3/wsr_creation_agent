"""Minimal PPTX renderer for approved customer-facing WSR content."""

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


class PptxRenderError(Exception):
    """Raised when customer-facing content cannot be rendered as PPTX."""


def render_wsr_pptx(content_sections: dict[str, object]) -> bytes:
    """Render customer-facing WSR sections into a basic PPTX document."""
    slide_lines = _content_lines(content_sections)
    if not slide_lines:
        raise PptxRenderError("No customer-facing content is available for export.")

    package = BytesIO()
    with ZipFile(package, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml())
        archive.writestr("_rels/.rels", _root_relationships_xml())
        archive.writestr("ppt/presentation.xml", _presentation_xml())
        archive.writestr("ppt/_rels/presentation.xml.rels", _presentation_relationships_xml())
        archive.writestr("ppt/slides/slide1.xml", _slide_xml(slide_lines))
    return package.getvalue()


def _content_lines(content_sections: dict[str, object]) -> list[str]:
    """Flatten relevant WSR sections into slide text lines."""
    ordered_keys = [
        "executiveSummary",
        "deliveryProgress",
        "keyAchievements",
        "risksAndDependenciesSummary",
        "nextWeekFocusAndActions",
        "customerFacingRemarks",
    ]
    lines = ["Weekly Status Report"]
    for key in ordered_keys:
        value = content_sections.get(key)
        if isinstance(value, str) and value.strip():
            lines.append(value.strip())
    return lines


def _content_types_xml() -> str:
    """Return required package content types for a single-slide PPTX."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml"
    ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slides/slide1.xml"
    ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
</Types>"""


def _root_relationships_xml() -> str:
    """Return root package relationships for the presentation document."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    Target="ppt/presentation.xml"/>
</Relationships>"""


def _presentation_xml() -> str:
    """Return the presentation document with one slide reference."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>
</p:presentation>"""


def _presentation_relationships_xml() -> str:
    """Return presentation relationships pointing to the only slide."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
    Target="slides/slide1.xml"/>
</Relationships>"""


def _slide_xml(lines: list[str]) -> str:
    """Return a simple text-only slide containing customer-facing WSR lines."""
    paragraphs = "\n".join(
        f"<a:p><a:r><a:t>{_escape_xml(line)}</a:t></a:r></a:p>" for line in lines
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr/>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="WSR Content"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:txBody><a:bodyPr/><a:lstStyle/>{paragraphs}</p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>"""


def _escape_xml(value: str) -> str:
    """Escape text for XML element content."""
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
