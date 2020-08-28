import re

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


def _convert_pdf_to_string_and_get_urls_from(file_path):
    external_links = []
    coordinates_and_info = []

    with open(file_path, "rb") as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            if page.annots:
                for annotation in page.annots:
                    if link_data := annotation.resolve().get("A"):
                        if uri := link_data.get("URI"):
                            external_links.append(uri.decode("utf-8"))

            interpreter.process_page(page)
            layout = device.get_result()
            for lobj in layout:
                if isinstance(lobj, LTTextBox):
                    x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
                    coordinates_and_info.append((y, x, re.sub(r"\s+", " ", text)))
    coordinates_and_info.sort(key=lambda tup: tup[0], reverse=True)  # sorts by y
    return ([elem[2] for elem in coordinates_and_info], external_links)
