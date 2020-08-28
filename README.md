# Resume Checker

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

You need to put the path of the resume that you want to analyze in `main.py` and run:

```sh
# Run the main script
pipenv run python main.py
```
