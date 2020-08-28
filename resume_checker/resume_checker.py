import re
from enum import Enum, auto
from itertools import tee
from typing import Any, Dict, List, Tuple

import requests
import spacy
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


def print_new_line_at_end(function_to_decorate):
    def wrapper(*args, **kw):
        function_to_decorate(*args, **kw)
        print()

    return wrapper


class Report:
    def __init__(
        self,
        correct_phone_number,
        sentences_information,
        verb_counter,
        dates,
        any_urls,
        broken_urls,
    ):
        self.correct_phone_number = correct_phone_number
        self.sentences_information = sentences_information
        self.verb_counter = verb_counter
        self.dates = dates
        self.any_urls = any_urls
        self.broken_urls = broken_urls

    def display_report(self):
        self._report_phone_number()
        self._report_metrics_and_bullet_per_sentence()
        self._report_sorted_dates()
        self._report_number_of_words()
        self._report_broken_links()

    @print_new_line_at_end
    def _report_phone_number(self):
        if not self.correct_phone_number:
            print("The phone number doesn't have the 52 country code")
        else:
            print("The phone number is in the correct format")

    @print_new_line_at_end
    def _report_metrics_and_bullet_per_sentence(self):
        for sentence_info in self.sentences_information:
            mistakes_in_sentence = []
            if (
                sentence_info.in_principal_section
                and not sentence_info.in_principal_section
            ):
                if not sentence_info.any_metrics:
                    mistakes_in_sentence.append(
                        "You don't have any metrics"
                        + "try to put some numbers and how impacted your work"
                    )
                if not sentence_info.bullet_word_at_the_beginning:
                    mistakes_in_sentence.append(
                        "You should start the sentence with a bullet word"
                    )
            if sentence_info.pronouns:
                mistakes_in_sentence.append(
                    "Try to not use any pronouns, we found this one: "
                    + " ".join(sentence_info.pronouns)
                )
            if mistakes_in_sentence:
                print(
                    f"The sentence: {sentence_info.sentence} has the following problems: "
                )
                print(*mistakes_in_sentence, sep="\n")

    @print_new_line_at_end
    def _report_sorted_dates(self):
        for date in self.dates:
            if not _is_sorted(date):
                print(
                    f"Some of your projects are not sorted, their initial dates are: {' '.join(date)}"
                )

    @print_new_line_at_end
    def _report_number_of_words(self):
        for _, category_counter in self.verb_counter.items():
            number_of_occurrences = [
                occurrences for _, occurrences in category_counter.items()
            ]
            average = sum(number_of_occurrences) / len(number_of_occurrences)
            verbs_above_average = [
                verb
                for verb, occurrences in category_counter.items()
                if occurrences > average
            ]
            if verbs_above_average:
                print(f"You are repeating too much: {' '.join(verbs_above_average)}.")

    @print_new_line_at_end
    def _report_broken_links(self):
        if self.broken_urls:
            print("We found some broken links:")
            print(*self.broken_urls, sep="\n")
        elif not self.any_urls:
            print("We didn't find any link, try to use them to link your projects/work")
        else:
            print("All your links all working propertly")


class SentenceInformation:
    __slots__ = (
        "sentence",
        "principal_section",
        "in_principal_section",
        "any_metrics",
        "pronouns",
        "bullet_word_at_the_beginning",
    )

    def __init__(self):
        self.sentence = ""
        self.principal_section = False
        self.in_principal_section = False
        self.any_metrics = False
        self.pronouns = []
        self.bullet_word_at_the_beginning = False


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
    (phone_checked, all_sentences, all_tenses_counter, dates_by_section) = _tokenize(
        _sorted_resume
    )
    # broken_urls = _url_checker(links)
    broken_urls = []

    report = Report(
        phone_checked,
        all_sentences,
        all_tenses_counter,
        dates_by_section,
        links is not None,
        broken_urls,
    )
    report.display_report()


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


def _tokenize(sentences: List[str]) -> Any:
    nlp = spacy.load("en_core_web_sm")
    phone_checked = False
    metrics_on = False

    dates_by_section: List[List[str]] = []
    temp_dates: List[str] = []

    all_tenses_counter: Dict[VerbTags, Dict[str, int]] = {
        VerbTags.VB: {},
        VerbTags.VBD: {},
        VerbTags.VBG: {},
    }
    all_sentences: List[SentenceInformation] = []
    correct_number = False

    for sentence in sentences:
        pronouns: List[str] = []
        sentence_information = SentenceInformation()

        if not phone_checked:
            phone_checked, correct_number = _is_phone(sentence)

        doc = nlp(sentence)
        sentence_information.sentence = sentence

        for word_information in doc:
            if pronoun := _is_pronoun(word_information.pos_, word_information.text):
                pronouns.append(pronoun)
        sentence_information.pronouns = pronouns

        metrics_status, principal_section = _is_section(sentence)

        if principal_section:
            if temp_dates:
                dates_by_section.append(temp_dates)
                temp_dates = []
            metrics_on = metrics_status
        sentence_information.principal_section = principal_section

        if metrics_on and not principal_section:
            past_verbs: List[str] = []
            participle_verb: List[str] = []
            present_verbs: List[str] = []
            check_bullet_word = True
            for token in doc:
                possible_bullet_or_verb = token.tag_

                bullet = _is_bullet_word(possible_bullet_or_verb)
                impact = _is_impact_word(possible_bullet_or_verb)
                present_verb = _is_verb(possible_bullet_or_verb)

                if check_bullet_word:
                    if present_verb and past_verbs or past_verbs and not present_verbs:
                        sentence_information.bullet_word_at_the_beginning = True
                        check_bullet_word = False
                    elif present_verb and not past_verbs:
                        check_bullet_word = False

                past_verbs.append(token.text) if bullet else None
                participle_verb.append(token.text) if impact else None
                present_verbs.append(token.text) if present_verb else None

            _words_to_dict(
                [
                    (VerbTags.VB, present_verbs),
                    (VerbTags.VBD, past_verbs),
                    (VerbTags.VBG, participle_verb),
                ],
                all_tenses_counter,
            )

            for ent in doc.ents:
                if date := _if_is_date_give_me_the_date(ent.label_, ent.text):
                    temp_dates.append(date)

                if _has_metrics(ent.label_):
                    sentence_information.any_metrics = True

        sentence_information.in_principal_section = metrics_on

        all_sentences.append(sentence_information)
    return (correct_number, all_sentences, all_tenses_counter, dates_by_section)


def _is_phone(string: str) -> Tuple[bool, bool]:
    phone_number = "".join([number for number in string if number.isdigit()])
    if not phone_number:
        return (False, False)
    if "52" not in phone_number[:-10]:
        return (True, False)
    else:
        return (True, True)


def _is_pronoun(class_word: str, word: str) -> str:
    return (
        word
        if any(t_word.name == class_word for t_word in UnivPosPronouns)
        and not any(i_pro.name == word.upper() for i_pro in IgnoredPronouns)
        else ""
    )


def _is_section(sentence: str) -> Tuple[bool, bool]:
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


def _has_metrics(label: str) -> bool:
    return any(m_label.name == label for m_label in NamedEntitiesMetric)


def _is_bullet_word(tag: str) -> bool:
    return tag == VerbTags.VBD.name


def _is_impact_word(tag: str) -> bool:
    return tag == VerbTags.VBG.name


def _is_verb(tag: str) -> bool:
    return tag == VerbTags.VB.name


def _if_is_date_give_me_the_date(tag: str, text: str) -> str:
    if tag == NamedEntityDate.DATE.name:
        for word in text.split():
            if len(only_first_number := re.sub(r"\D", "", word)) > 2:
                return only_first_number
    return ""


def _is_sorted(date: List[int]) -> bool:
    l1, l2 = tee(date)
    next(l2, None)
    return all(a >= b for a, b in zip(l1, l2))


def _words_to_dict(
    list_of_type_words: List[Tuple[VerbTags, List[str]]], all_tenses_counter,
) -> None:
    for type_words in list_of_type_words:
        word_type, list_words = type_words
        for word in list_words:
            category = all_tenses_counter.get(word_type)
            if inserted_word := category.get(word):
                category[word] = inserted_word + 1
            else:
                category[word] = 1


def _url_checker(urls: List[str]) -> List[str]:
    broken_urls = []
    for index, url in enumerate(urls):
        if "mailto" not in url:
            print(f"Checking {index} of {len(urls)} urls", end="\r", flush=True)
            r = requests.head(url)
            if r.status_code == 404 or r.status_code == 503:
                broken_urls.append(url)
    return broken_urls


def fib(n: int) -> int:
    if n < 2:
        return n
    else:
        return fib(n - 1) + fib(n - 2)
