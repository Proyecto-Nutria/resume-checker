from resume_checker.pdf import _convert_pdf_to_string_and_get_urls_from

preview_pdf = "./test/test_pdf/preview.pdf"


def test_no_pdf():
    assert _convert_pdf_to_string_and_get_urls_from(preview_pdf) == (
        ["Some text ", "Some text ", "A link ", "A links "],
        ["http://www.google.com/", "http://www.twitter.com/"],
    )
