from resume_checker.network import _url_checker

url_and_email = ["http://www.google.com", "mailto:nutria@gmial.com"]
urls_200 = ["http://www.google.com", "http://www.twitter.com"]
urls_404 = ["https://www.google.com/secrets"]


def test_no_urls():
    assert _url_checker([]) == []


def test_url_and_mail():
    assert _url_checker(url_and_email) == []


def test_404_page():
    assert _url_checker(urls_404) == urls_404


def test_200_pages():
    assert _url_checker(urls_200) == []
