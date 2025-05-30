import markdown2
import pdfkit
from docx import Document
import os

def export_to_pdf(markdown_text, output_path="uploads/output.pdf"):
    html = markdown2.markdown(markdown_text)
    pdfkit.from_string(html, output_path)
    return output_path

def export_to_docx(markdown_text, output_path="uploads/output.docx"):
    doc = Document()
    for line in markdown_text.splitlines():
        doc.add_paragraph(line)
    doc.save(output_path)
    return output_path

def export_to_md(markdown_text, output_path="uploads/output.md"):
    with open(output_path, "w") as f:
        f.write(markdown_text)
    return output_path
