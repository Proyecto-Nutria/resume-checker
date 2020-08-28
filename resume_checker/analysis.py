import re
from enum import Enum, auto
from typing import Any, Dict, List, Tuple

import spacy

from resume_checker.structure import SentenceInformation


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
