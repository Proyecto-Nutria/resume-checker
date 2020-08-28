# This package was created with: https://github.com/sourcery-ai/python-best-practices-cookiecutter

from resume_checker.analysis import _tokenize
from resume_checker.network import _url_checker
from resume_checker.output import Report
from resume_checker.pdf import _convert_pdf_to_string_and_get_urls_from


def create_report_of(filepath):

    _sorted_resume, links = _convert_pdf_to_string_and_get_urls_from(filepath)
    (phone_checked, all_sentences, all_tenses_counter, dates_by_section) = _tokenize(
        _sorted_resume
    )
    broken_urls = _url_checker([])  # links
    report = Report(
        phone_checked,
        all_sentences,
        all_tenses_counter,
        dates_by_section,
        links is not None,
        broken_urls,
    )
    report.display_report()
