import hashlib
from typing import Dict, List, Tuple

from src.processing.models.Replace import Replace
from nltk import sent_tokenize


def fix_pos_tagging(tags: List[Tuple[str, str]], rules: List[Dict]) -> List[Dict]:
    """
    Loads a dictionary of words which can have wrong POS tag after tagging.
    Changes wrong tag for word in list of tuples of noun-tag

    Example actor is recognized by nltk as adjective, meanwhile it's a noun.

    :argument
    tags -- a list with tuples word-tag

    :argument
    rules --dictionary of rules to fix wrong POS tagging from nltk

    :returns
    List of rules to change tags
    """
    for tag in tags:
        for rule in rules:
            if rule['word'] == tag[0].lower() and tag[1] == rule['posTag']:
                index = tags.index(tag)
                tags[index] = (tag[0], rule['changeTo'])
    return rules


def prepare_sentence_for_tagging(sentence: str, contractions: Dict[str, str]) -> (List[str], List[Replace]):
    """
    Attention! Changes the initial sentence
    Applies contractions from contractions dictionary to sentence
    Changes apostrophe, ), ( as they affect parsing sentence to tree

    :argument
    sentence -- a sentence to change

    :argument
    contractions -- a dictionary of contractions of type it's -> it is

    :returns
    Changed sentence (i.e list of tokens), list of replaces made
    """
    symbols = ['(', ')', '/', '}', '{', '.', ',', ":", ";", "?", '!']
    replaces: List[Replace] = []
    replaced_sentence_tokens = []

    for index, word in enumerate(sentence.split()):
        unified_word = word.lower().replace("`", "'").replace("’", "'")
        rep: Replace
        has_changed_symbols = False
        for symbol in symbols:
            if symbol in unified_word:
                rep = Replace(len(replaced_sentence_tokens), 1, word)
                if symbol == '/':
                    unified_word = unified_word.replace('/', 'or')
                if symbol == '}':
                    unified_word = unified_word.replace('}', 'and')
                if symbol == '{':
                    unified_word = unified_word.replace('{', 'and')
                else:
                    unified_word = unified_word.translate({ord(ch): '' for ch in symbols})
                has_changed_symbols = True
                break

        if unified_word in contractions.keys():
            replace_words = contractions[unified_word].split()
            rep = Replace(len(replaced_sentence_tokens), len(replace_words), word)
            replaces.append(rep)
            replaced_sentence_tokens += replace_words
        else:
            if has_changed_symbols:
                replaces.append(rep)
                replaced_sentence_tokens.append(unified_word)
            else:
                replaced_sentence_tokens.append(word)
    return replaced_sentence_tokens, replaces


def md5(string):
    """
    :returns
    hash of a sentence to save as cache key
    """
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def get_sentence_tokens(text: str) -> List[str]:
    """
    Tokenizes a text to sentence tokens

    :argument
    text -- text to tokenize

    :returns
    tokens
    """
    lines = text.split('\n')
    tokenized = []
    for line in lines:
        if line == '':
            tokenized.append(line)
        else:
            tokenized += sent_tokenize(line)
            tokenized.append('')
    tokenized.pop(len(tokenized) - 1)
    return tokenized
