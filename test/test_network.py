from unittest.mock import patch

from resume_checker.network import _url_checker

url_and_email = ["http://www.google.com", "mailto:nutria@gmial.com"]
urls_200 = ["http://www.google.com", "http://www.twitter.com"]
urls_404 = ["https://www.sergio-bot.com/"]
urls_503 = ["https://www.manuel-bot.com/"]


def test_no_urls():
    assert _url_checker([]) == []


def test_url_and_mail():
    with patch("requests.head") as mock_request:
        mock_request.return_value.status_code = 200
        assert _url_checker(url_and_email) == []


def test_200_pages():
    with patch("requests.head") as mock_request:
        mock_request.return_value.status_code = 200
        assert _url_checker(urls_200) == []


def test_404_page():
    with patch("requests.head") as mock_request:
        mock_request.return_value.status_code = 404
        assert _url_checker(urls_404) == urls_404


def test_503_page():
    with patch("requests.head") as mock_request:
        mock_request.return_value.status_code = 503
        assert _url_checker(urls_503) == urls_503
