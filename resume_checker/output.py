from itertools import tee


def print_new_line_at_end(function_to_decorate):
    def wrapper(*args, **kw):
        function_to_decorate(*args, **kw)
        print()

    return wrapper


class Report:
    def __init__(
        self,
        correct_phone_number,
        sentences_information,
        verb_counter,
        dates,
        any_urls,
        broken_urls,
    ):
        self.correct_phone_number = correct_phone_number
        self.sentences_information = sentences_information
        self.verb_counter = verb_counter
        self.dates = dates
        self.any_urls = any_urls
        self.broken_urls = broken_urls

    def display_report(self):
        self._report_phone_number()
        self._report_metrics_and_bullet_per_sentence()
        self._report_sorted_dates()
        self._report_number_of_words()
        self._report_broken_links()

    @print_new_line_at_end
    def _report_phone_number(self):
        if not self.correct_phone_number:
            print("The phone number doesn't have the 52 country code")
        else:
            print("The phone number is in the correct format")

    @print_new_line_at_end
    def _report_metrics_and_bullet_per_sentence(self):
        for sentence_info in self.sentences_information:
            mistakes_in_sentence = []
            if (
                sentence_info.in_principal_section
                and not sentence_info.in_principal_section
            ):
                if not sentence_info.any_metrics:
                    mistakes_in_sentence.append(
                        "You don't have any metrics"
                        + "try to put some numbers and how impacted your work"
                    )
                if not sentence_info.bullet_word_at_the_beginning:
                    mistakes_in_sentence.append(
                        "You should start the sentence with a bullet word"
                    )
            if sentence_info.pronouns:
                mistakes_in_sentence.append(
                    "Try to not use any pronouns, we found this one: "
                    + " ".join(sentence_info.pronouns)
                )
            if mistakes_in_sentence:
                print(
                    f"The sentence: {sentence_info.sentence} has the following problems: "
                )
                print(*mistakes_in_sentence, sep="\n")

    @print_new_line_at_end
    def _report_sorted_dates(self):
        for date in self.dates:
            if not self._is_sorted(date):
                print(
                    f"Some of your projects are not sorted, their initial dates are: {' '.join(date)}"
                )

    def _is_sorted(self, date):
        l1, l2 = tee(date)
        next(l2, None)
        return all(a >= b for a, b in zip(l1, l2))

    @print_new_line_at_end
    def _report_number_of_words(self):
        for _, category_counter in self.verb_counter.items():
            number_of_occurrences = [
                occurrences for _, occurrences in category_counter.items()
            ]
            if number_of_occurrences:
                average = sum(number_of_occurrences) / len(number_of_occurrences)
                verbs_above_average = [
                    verb
                    for verb, occurrences in category_counter.items()
                    if occurrences > average
                ]
                if verbs_above_average:
                    print(
                        f"You are repeating too much: {' '.join(verbs_above_average)}."
                    )

    @print_new_line_at_end
    def _report_broken_links(self):
        if self.broken_urls:
            print("We found some broken links:")
            print(*self.broken_urls, sep="\n")
        elif not self.any_urls:
            print("We didn't find any link, try to use them to link your projects/work")
        else:
            print("All your links all working propertly")
