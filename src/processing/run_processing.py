import json
import os
from typing import List

from src.processing.models.Preloading import Preloading
from src.processing.models.dtos import SentenceDto
from src.processing.processor import process_tree
from src.processing.utils.load_utils import download_nltk_modules, load_contractions, load_rules_fix_pos_tagging, \
    load_uncountable_nouns_list, load_dictionaries
from src.processing.utils.preprocessing_utils import md5, get_sentence_tokens
from src.processing.utils.tree_processing_utils import get_tree_from_sentence


def process_sentence(phrase: str, preloading: Preloading) -> SentenceDto:
    """
    Runs the program to check one sentence

    :argument
    phrase -- a sentence where missing articles are investigated

    :returns
    List of suggestions with start and end of NP and possible article replacements
    """
    if phrase == '':
        return {'text': '\n', 'suggestions': []}

    if not preloading.modules_updated:
        download_nltk_modules()
    if not preloading.contractions:
        preloading.contractions = load_contractions()
    if not preloading.rules_fix_pos_tagging:
        preloading.rules_fix_pos_tagging = load_rules_fix_pos_tagging()
    if not preloading.uncountable_nouns_list:
        preloading.uncountable_nouns_list = load_uncountable_nouns_list()

    tree, replaces = get_tree_from_sentence(phrase, preloading)
    suggestions = process_tree(phrase, tree, replaces, preloading.uncountable_nouns_list)
    return suggestions


def process_text(text: str, use_cache: bool = False) -> List[SentenceDto]:
    """
    Runs the program to check text

    :argument
    text -- text where missing articles are investigated

    :argument
    use_cache -- whether cache is needed to use, experimental

    :returns
    List of suggestions with start and end of NP and possible article replacements
    """
    modules_updated: bool = download_nltk_modules()
    contractions, rules_fix_pos_tagging, uncountable_nouns_list = load_dictionaries()
    preloading = Preloading(contractions, rules_fix_pos_tagging, uncountable_nouns_list, modules_updated)
    if not use_cache:
        list_of_sentences = get_sentence_tokens(text)
        answer: List[SentenceDto] = []
        for phrase in list_of_sentences:
            result_for_sentence = process_sentence(phrase, preloading)
            answer.append(result_for_sentence)
    else:
        answer = process_text_with_cache(text, preloading)

    return answer


def process_text_with_cache(text: str, preloading: Preloading) -> List[SentenceDto]:
    """
    Runs the program to check text using/adding cache

    :argument
    text -- text where missing articles are investigated

    :returns
    List of suggestions with start and end of NP and possible article replacements
    """
    hashes_json = os.path.join(os.path.dirname(__file__), "../../resources/dictionaries/hashes.json")
    if os.path.exists(hashes_json):
        with open(hashes_json, "r") as f:
            hashes_exist = f.read()
        cache = json.loads(hashes_exist)
    else:
        cache = {}

    list_of_sentences = get_sentence_tokens(text)
    answer: List[SentenceDto] = []

    for phrase in list_of_sentences:
        md5_phrase = md5(phrase)
        if md5_phrase in cache.keys():
            is_added = False
            for entry in cache[md5_phrase]:
                if phrase in entry['text']:
                    answer.append(entry)
                    is_added = True
                    break
            if not is_added:
                result_for_sentence = process_sentence(phrase, preloading)
                answer.append(result_for_sentence)
                cache[md5_phrase].append(result_for_sentence)
        else:
            result_for_sentence = process_sentence(phrase, preloading)
            answer.append(result_for_sentence)
            cache[md5_phrase] = [result_for_sentence]

    cache = json.dumps(cache)
    with open(hashes_json, "w") as f:
        f.write(cache)

    return answer

