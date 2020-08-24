from enum import Enum
from io import StringIO

import spacy
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


class TypeWords(Enum):
    PRONOUN = "PRON"


class IgnoredPronoun(Enum):
    IT = "it"


def create_report_of(filepath):

    resume_as_lines, links = _convert_pdf_to_string_and_get_urls_from(filepath)
    resume_as_array = _split_and_clean_string(resume_as_lines)
    _tokenize(resume_as_array)


def _convert_pdf_to_string_and_get_urls_from(file_path):
    output_string = StringIO()
    external_links = []

    with open(file_path, "rb") as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            if page.annots:
                for annotation in page.annots:
                    if link_data := annotation.resolve().get("A"):  # fmt: off
                        if uri := link_data.get("URI"):
                            external_links.append(uri.decode("utf-8"))
            interpreter.process_page(page)
    return (output_string.getvalue(), external_links)


def _split_and_clean_string(resume_info):
    return (
        non_empty
        for non_empty in (
            " ".join(split_line.split()) for split_line in resume_info.splitlines()
        )
        if non_empty
    )


def _tokenize(sentences):
    nlp = spacy.load("en_core_web_sm")
    phone_checked = False
    for sentence in sentences:
        doc = nlp(sentence)
        if not phone_checked:
            phone_checked = _is_phone(sentence)

        """
        for ent in doc.ents:
            print(f"{ent.text} {ent.start_char} {ent.end_char} {ent.label}")
        """

        pronouns = []
        for word_information in doc:
            word = word_information.text
            if pronoun := _is_pronoun(word_information.pos_, word):
                pronouns.append(pronoun)

        print(pronouns)


def _is_phone(string):
    phone_number = "".join([number for number in string if number.isdigit()])
    if not phone_number:
        return False
    if "52" not in phone_number[:-10]:
        print("Wrong Number")
    else:
        print("Correct Number")
    return True


def _is_pronoun(class_word, word):
    return (
        word
        if class_word == TypeWords.PRONOUN.value
        and word.lower() != IgnoredPronoun.IT.value
        else None
    )


def fib(n: int) -> int:
    if n < 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)
