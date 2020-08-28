# Resume Checker

## Setup

```sh
# Install dependencies
pipenv install --dev

# Setup pre-commit and pre-push hooks
pipenv run pre-commit install -t pre-commit
pipenv run pre-commit install -t pre-push
pipenv run python -m spacy download en_core_web_sm
```
