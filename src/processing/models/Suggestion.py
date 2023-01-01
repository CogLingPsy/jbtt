from typing import List

from src.processing.models.dtos import SuggestionDto


class Suggestion:
    def __init__(
            self,
            start: int,
            end: int,
            replacements: List[str],
            cause: str
    ):
        self.start = start
        self.end = end
        self.replacements = replacements
        self.cause = cause

    def shift(self, length: int):
        """ Shift of suggestion to number of words (=length) """
        self.start += length
        self.end += length

    def get_suggestion_dto(self, sentence: List[str]) -> SuggestionDto:
        """ Form suggestion: start letter of NP, end letter of NP and possible articles """
        start_char = sum([len(words) for words in sentence[:self.start]]) + self.start
        end_char = sum([len(words) for words in sentence[self.start:self.end]]) + start_char + self.end - self.start - 1
        return {
            'start': start_char,
            'end': end_char,
            'replacements': self.replacements,
            'cause': self.cause
        }
