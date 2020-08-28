from resume_checker.analysis import (
    _has_metrics,
    _if_is_date_give_me_the_date,
    _is_bullet_word,
    _is_impact_word,
    _is_phone,
    _is_pronoun,
    _is_section,
    _is_verb,
)


def test_number():
    correct_number = "525556565656"
    incorrect_number_no_code = "56565656"
    incorrect_number_bad_code = "5556565656"
    assert _is_phone(correct_number) == (True, True)
    assert _is_phone(incorrect_number_no_code) == (True, False)
    assert _is_phone(incorrect_number_bad_code) == (True, False)


def test_pronouns():
    assert _is_pronoun("PRON", "I") == "I"
    assert _is_pronoun("PRON", "It") == ""


def test_metric_sections():
    sections = ["Projects", "Professional Work"]
    ignored_metric_sections = ["Education", "About Me", "Skills"]
    assert all(_is_section(section) == (True, True) for section in sections)
    assert all(
        _is_section(ignored) == (False, True) for ignored in ignored_metric_sections
    )
    assert _is_section("This is not a section") == (False, False)


def test_has_metrics():
    metric_labels = ["PERCENT", "MONEY", "ORDINAL", "CARDINAL"]
    non_metric_labels = ["ORG", "DATE"]
    assert all(_has_metrics(label) for label in metric_labels)
    assert not all(_has_metrics(label) for label in non_metric_labels)


def test_words():
    assert _is_bullet_word("VBD")
    assert _is_impact_word("VBG")
    assert _is_verb("VB")


def test_date_give_me_the_date():
    assert _if_is_date_give_me_the_date("DATE", "May 2020") == "2020"
    assert _if_is_date_give_me_the_date("CARDINAL", "2020") == ""
