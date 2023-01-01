from typing import Dict, List


class Preloading:
    """ Object containing info about loaded dictionaries """
    def __init__(self, contractions: Dict[str, str], rules_fix_pos_tagging: List[Dict],
                 uncountable_nouns_list: List[str], modules_updated: bool):
        self.contractions = contractions
        self.rules_fix_pos_tagging = rules_fix_pos_tagging
        self.uncountable_nouns_list = uncountable_nouns_list
        self.modules_updated = modules_updated
