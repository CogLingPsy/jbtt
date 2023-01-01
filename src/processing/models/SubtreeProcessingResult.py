from typing import List

from src.processing.models.Replace import Replace
from src.processing.models.Suggestion import Suggestion
from src.processing.models.dtos import SentenceDto


class SubtreeProcessingResult:
    """ Object containing info about article resolution for one NP """
    def __init__(
            self,
            words: List[str],
            suggestions: List[Suggestion]
    ):
        self.words = words
        self.suggestions = suggestions

    def words_count(self) -> int:
        """ Count of words in NP """
        return len(self.words)

    def shift(self, length: int):
        """ Shift for subtrees relatively the previous one from second one """
        for suggestion in self.suggestions:
            suggestion.shift(length)

    def __shift_affected__(self, index: int, length: int):
        """ Shift for words after the index inside subtree because of replace """
        for suggestion in self.suggestions:
            if suggestion.start > index:
                suggestion.shift(length)

    def concat(self, other):
        """ Concatenation of two subtrees """
        other: SubtreeProcessingResult
        other.shift(self.words_count())
        self.words += other.words
        self.suggestions += other.suggestions

    def apply_replace(self, replace: Replace):
        """ Return this part of sentence to initial state """
        for _ in range(0, replace.words_in_replace):
            self.words.pop(replace.index)
        self.words.insert(replace.index, replace.original)
        self.__shift_affected__(replace.index, -(replace.words_in_replace - 1))

    def get_sentence(self, phrase) -> SentenceDto:
        """ Return result of processing """
        suggestions = []
        for suggestion in self.suggestions:
            suggestions.append(suggestion.get_suggestion_dto(self.words))
        return {
            'text': phrase,
            'suggestions': suggestions
        }