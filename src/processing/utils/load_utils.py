import os, json
from typing import Dict, List, Tuple
import nltk


def load_contractions() -> Dict[str, str]:
    """
    Loads a dictionary of contractions to improve POS tagging in future.
    Example it's -> it is

    :returns
    Dictionary of contractions
    """
    with open(os.path.join(os.path.dirname(__file__), "../../../resources/dictionaries/contractions.json")) as f:
        contractions_raw: str = f.read()
        contractions: Dict[str, str] = json.loads(contractions_raw)
    return contractions


def load_rules_fix_pos_tagging() -> List[Dict]:
    """
    Loads a dictionary of rules to improve POS tagging in future.

    :returns
    Dictionary of rules to fix wrong POS tagging from nltk
    """
    with open(os.path.join(os.path.dirname(__file__), "../../../resources/dictionaries/fix_pos_tagging_dict.json")) as f:
        fix_rules_raw: str = f.read()
        rules: List[Dict] = json.loads(fix_rules_raw)
    return rules


def load_uncountable_nouns_list() -> List[str]:
    """
    Loads a "dictionary" of uncountable nouns

    :returns
    List of uncountable nouns
    """
    with open(os.path.join(os.path.dirname(__file__), "../../../resources/dictionaries/uncountable_nouns_list.json")) as f:
        uncountable_nouns_raw = f.read()
        uncountable_nouns_list = json.loads(uncountable_nouns_raw)['nouns']
    return uncountable_nouns_list


def download_nltk_modules() -> bool:
    """
    Downloads necessary nltk modules if not exist
    """
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger')

    try:
        nltk.data.find('chunkers/maxent_ne_chunker')
    except LookupError:
        nltk.download('maxent_ne_chunker')

    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words')

    return True


def load_dictionaries() -> Tuple[Dict[str, str], List[dict], List[str]]:
    """
    Loads necessary dictionaries for preprocessing
    """
    contractions: Dict[str, str] = load_contractions()
    rules_fix_pos_tagging: List[Dict] = load_rules_fix_pos_tagging()
    uncountable_nouns_list: List[str] = load_uncountable_nouns_list()
    return contractions, rules_fix_pos_tagging, uncountable_nouns_list
