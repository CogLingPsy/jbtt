from typing import TypedDict, List


class SuggestionDto(TypedDict):
    """ Suggestion containing NP with article and positions of start and end of NP """
    start: int
    end: int
    replacements: List[str]
    cause: str


class SentenceDto(TypedDict):
    """ Object containing original text and list of SuggestionDto """
    text: str
    suggestions: List[SuggestionDto]
