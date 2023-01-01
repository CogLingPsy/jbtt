class Replace:
    """ Object containing info about replaces made in original sentence """
    def __init__(self, index: int, words_in_replace: int, original: str):
        self.index = index
        self.words_in_replace = words_in_replace
        self.original = original