import re
from enum import Enum, auto
from itertools import tee

import spacy
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


class VerbTags(Enum):
    VB = "base"  # Base
    VBD = "past"  # Past
    VBG = "gerund"  # verb, gerund or present participle


class IgnoredPronouns(Enum):
    IT = auto()


class UnivPosPronouns(Enum):
    PRON = auto()


class NamedEntitiesMetric(Enum):
    PERCENT = auto()
    MONEY = auto()
    ORDINAL = auto()
    CARDINAL = auto()


class NamedEntityDate(Enum):
    DATE = auto()


class StemSectionsMetric(Enum):
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


class StemSectionsIgnoredMetric(Enum):
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

    dates_by_section = []
    temp_dates = []

    all_tenses = {VerbTags.VB: {}, VerbTags.VBD: {}, VerbTags.VBG: {}}

    for sentence in sentences:
        pronouns = []
        past_verbs = []
        participle_verb = []
        present_verbs = []

        if not phone_checked:
            phone_checked = _is_phone(sentence)

        doc = nlp(sentence)

        for word_information in doc:
            word = word_information.text
            if pronoun := _is_pronoun(word_information.pos_, word):
                pronouns.append(pronoun)

        metrics_status, principal_section = _is_section(sentence)

        if principal_section:
            if temp_dates:
                dates_by_section.append(temp_dates)
                temp_dates = []
            metrics_on = metrics_status

        if metrics_on and not principal_section:
            for token in doc:
                possible_bullet_or_verb = token.tag_

                bullet = _is_bullet_word(possible_bullet_or_verb)
                impact = _is_impact_word(possible_bullet_or_verb)
                present_verb = _is_verb(possible_bullet_or_verb)

                if present_verb and not past_verbs:
                    print(sentence)
                    print("Try to use bullet words as yor first word")

                past_verbs.append(token.text) if bullet else None
                participle_verb.append(token.text) if impact else None
                present_verbs.append(token.text) if present_verb else None

            for ent in doc.ents:
                if date := _if_is_date_give_me_the_date(ent.label_, ent.text):
                    temp_dates.append(date)

        _words_to_dict(
            [
                (VerbTags.VB, present_verbs),
                (VerbTags.VBD, past_verbs),
                (VerbTags.VBG, participle_verb),
            ],
            all_tenses,
        )

    print(f"{all_tenses}")
    print(f"{_is_sorted(dates_by_section)}")


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
        if any(t_word.name == class_word for t_word in UnivPosPronouns)
        and not any(i_pro.name == word.lower() for i_pro in IgnoredPronouns)
        else None
    )


def _is_section(sentence):
    # Sections in general have at most 3 words
    if len(possible_section := sentence.split()) < 4:
        str_section = " ".join(possible_section)
        if any(
            section in str_section.lower()
            for category in StemSectionsMetric
            for section in category.value
        ):
            return (True, True)
        elif any(
            section in str_section.lower()
            for category in StemSectionsIgnoredMetric
            for section in category.value
        ):
            return (False, True)
    return (False, False)


def _has_metrics(label):
    return any(m_label.name == label for m_label in NamedEntitiesMetric)


def _is_bullet_word(tag):
    return tag == VerbTags.VBD.name


def _is_impact_word(tag):
    return tag == VerbTags.VBG.name


def _is_verb(tag):
    return tag == VerbTags.VB.name


def _if_is_date_give_me_the_date(tag, text):
    if tag == NamedEntityDate.DATE.name:
        for word in text.split():
            if len(only_first_number := re.sub(r"\D", "", word)) > 2:
                return only_first_number
    return None


def _is_sorted(all_dates):
    for date in all_dates:
        print(f"{date}")
        l1, l2 = tee(date)
        next(l2, None)
        print(all(a >= b for a, b in zip(l1, l2)))


def _words_to_dict(list_of_type_words, all_tenses):
    for type_words in list_of_type_words:
        word_type, list_words = type_words
        for word in list_words:
            category = all_tenses.get(word_type)
            if inserted_word := category.get(word):
                category[word] = inserted_word + 1
            else:
                category[word] = 1


def fib(n: int) -> int:
    if n < 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)
