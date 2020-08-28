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
