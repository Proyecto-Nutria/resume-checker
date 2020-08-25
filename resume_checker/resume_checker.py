import re
from enum import Enum, auto

import spacy
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


class IgnoredPronouns(Enum):
    IT = auto()


class TypeWords(Enum):
    PRON = auto()


class Metrics(Enum):
    PERCENT = auto()
    MONEY = auto()
    ORDINAL = auto()
    CARDINAL = auto()


class MetricSectionsStem(Enum):
    WORK = {
        "work",
        "experi",
    }
    EDUCATION = {
        "research",
        "project",
    }
    PERSONAL = {
        "leader",
        "award",
        "volunt",
    }


class IgnoredMetricSectionsStem(Enum):
    EDUCATION = {
        "educ",
        "cours",
        "certif",
        "languag",
    }
    PERSONAL = {
        "skill",
        "techno",
        "about",
        "hobbi",
        "event",
        "hackaton",
        "interest",
        "activities",
    }
    EXTRA = {
        "other",
    }


def create_report_of(filepath):

    _sorted_resume, links = _convert_pdf_to_string_and_get_urls_from(filepath)
    _tokenize(_sorted_resume)


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


def _tokenize(sentences):
    nlp = spacy.load("en_core_web_sm")
    phone_checked = False
    metrics_on = False

    for sentence in sentences:

        if not phone_checked:
            phone_checked = _is_phone(sentence)

        doc = nlp(sentence)

        pronouns = []
        for word_information in doc:
            word = word_information.text
            if pronoun := _is_pronoun(word_information.pos_, word):
                pronouns.append(pronoun)

        metrics_status, principal_section = _is_section(sentence)

        if principal_section:
            metrics_on = metrics_status

        if metrics_on and not principal_section:
            for ent in doc.ents:
                if _has_metrics(ent.label_):
                    print(f"Labeled:{ent.text} || {ent.label_}")


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
        if any(t_word.name == class_word for t_word in TypeWords)
        and not any(i_pro.name == word.lower() for i_pro in IgnoredPronouns)
        else None
    )


def _is_section(sentence):
    # The sections in most of the resumes have at most 3 words
    if len(possible_section := sentence.split()) < 4:
        str_section = " ".join(possible_section)
        if any(
            section in str_section.lower()
            for category in MetricSectionsStem
            for section in category.value
        ):
            return (True, True)
        elif any(
            section in str_section.lower()
            for category in IgnoredMetricSectionsStem
            for section in category.value
        ):
            return (False, True)
    return (False, False)


def _has_metrics(label):
    return any(m_label.name == label for m_label in Metrics)


def fib(n: int) -> int:
    if n < 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)
