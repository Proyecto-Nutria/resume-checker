# Resume Checker
![Tests]https://github.com/Proyecto-Nutria/resume-checker/workflows/Test/badge.svg

Tool that analyze technical resumes and generates human readable feedback.

### Features

1. Phone number with the correct area code
1. Bullet words and analytics in the sentences
1. Experience/Projects sorted by date
1. Words that appear in an excessive amount

### Setup

```sh
# Install dependencies
pipenv install --dev

# Setup pre-commit and pre-push hooks
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
pipenv run python -m spacy download en_core_web_sm

```

### Usage

```sh
# Run the main script to analyze the resume
pipenv run python -m resume_checker "resume.pdf"
```
