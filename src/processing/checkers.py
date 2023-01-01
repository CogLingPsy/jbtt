import re
from typing import List

import nltk


def is_determinative_in_group(leaves: List[str]) -> bool:
    """
    Check if there is some determinative in noun group (NP).
    Presence means no additional determinative should be inserted

    :argument
    leaves -- list of POS tags in NP

    :returns
    True if article, possessive or demonstrative pronoun or cardinal number in NP, else False
    """
    return 'DT' in leaves or 'PRP$' in leaves or 'CD' in leaves


def resolve_vowel(word: str) -> str:
    """
    Check if a word after the indefinite article starts with vowel.
    If starts - article should be "an", otherwise "a"

    To improve: a/an before letter "u", because it could be both:
    a university (first sound is j, /juːnɪˈvɜːsəti/)
    an umbrella (first sound is ʌ, /ʌmˈbɹɛlə/)

    :argument
    word -- a word to process

    :returns
    Article
    """

    if word.lower()[0] in ('a', 'e', 'i', 'o', 'u'):
        return 'an'
    else:
        return 'a'


def is_noun_plural(leaves: List[str]) -> bool:
    """
    Check if a noun is plural. In this case the indefinite article is not applicable.

    :argument
    leaves -- list of POS tags in NP

    :returns
    True, if noun is plural, else False
    """
    return 'NNS' in leaves or 'NNPS' in leaves


def is_jj_superlative(leaves: List[str]) -> bool:
    """
    Check if an adjective is superlative. In this case the definite article is applicable.

    :argument
    leaves -- list of POS tags in NP

    :returns
    True, if adjective is superlative, else False
    """
    return 'JJS' in leaves


def is_noun_uncountable(subtree: nltk.Tree, uncountable_nouns_list: List[str]) -> bool:
    """
    Check if a noun is uncountable. In this case articles are not applicable.

    :argument
    subtree -- a noun group with POS tagging
    
    :argument
    uncountable_nouns_list -- list containing uncountable nouns

    :returns
    True, if noun is uncountable, else False
    """

    rx = re.compile(r'(.*\/NN.*)')
    noun_type = re.sub('[,|!|.]', '',
                       list(filter(rx.match, subtree.leaves()))[0].split('/', maxsplit=1)[0].capitalize())
    return noun_type in uncountable_nouns_list


def is_named_entity(tree_leaves: List[str]) -> bool:
    """
    Check if a noun is Named Entity. In this case articles are not applicable.

    :argument
    tree_leaves -- a noun group with POS tagging

    :returns
    True, if noun is Named Entity, else False
    """
    for leaf in tree_leaves:
        if leaf.count('/') == 3:
            return True
    return False


def has_unique_jj(words_leaves: List[str], pos_leaves: List[str]) -> bool:
    """
    Check if an adjective means something unique. In this case the definite article is applicable.

    :argument
    words_leaves -- a noun group
    :argument
    pos_leaves -- list of POS tags in NP

    :returns
    True, if adjective is unique, else False
    """
    unique_jj = ('same', 'main', 'whole', 'previous', 'right', 'next', 'left', 'last', 'only', 'wrong')
    if 'JJ' in pos_leaves:
        if words_leaves[pos_leaves.index('JJ')].lower() in unique_jj:
            return True
    return False


def is_a_group_of(words_leaves: List[str]) -> bool:
    """
    Check if NP represents a collocation of type 'a group of', 'a herd of'.
    In this case articles are not applicable.

    :argument
    words_leaves -- a noun group

    :returns
    True, if collocation under question, else False
    """
    return len(words_leaves) >= 3 and words_leaves[0] == 'a' and words_leaves[2] == 'of'


def is_quantity_of(words_leaves: List[str]) -> bool:
    """
    Check if NP represents a collocation of type 'all of', 'none of'.
    In this case the definite article is applicable.

    :argument
    words_leaves -- a noun group

    :returns
    True, if collocation under question, else False
    """
    return words_leaves[0].lower() in ('all', 'none', 'both') and words_leaves[1] == 'of'
