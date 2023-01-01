from typing import List

import nltk
from nltk import Tree
import copy

from src.processing.models.Preloading import Preloading
from src.processing.models.Replace import Replace
from src.processing.checkers import is_noun_plural, is_jj_superlative, has_unique_jj, resolve_vowel
from src.processing.models.SubtreeProcessingResult import SubtreeProcessingResult
from src.processing.models.Suggestion import Suggestion
from src.processing.preprocessing import pos_tagging, create_tree_from_grammar


def get_tree_from_sentence(phrase: str, preloading: Preloading) -> (nltk.Tree, List[Replace]):
    """
    Processes string into tree

    :argument
    phrase -- a string to convert in a tree
    :argument
    preloading -- object containing dictionaries

    :returns
    Tree representation of phrase, lst of made replaces in it
    """

    tags, replaces = pos_tagging(phrase, preloading)
    tree: nltk.Tree = create_tree_from_grammar(tags)
    return tree, replaces


def get_words_leaves(tree_leaves: List[str]) -> List[str]:
    """
    Extracts words from tree with tuples word-tag

    :argument
    tree_leaves -- list with word/tag elements

    :returns
    List of words
    """
    leaves: List[str] = []
    for leaf in tree_leaves:
        leaves.append(leaf.split('/')[0])
    return leaves


def get_pos_leaves(tree_leaves: List[str]) -> List[str]:
    """
    Extracts POS tags from tree with tuples word-tag

    :argument
    tree_leaves -- list with word/tag elements

    :returns
    List of tags
    """
    leaves: List[str] = []
    for leaf in tree_leaves:
        leaves.append(leaf.split('/')[1])
    return leaves


def insert_article_in_tree(position: int, article: str, words_leaves: List[str], rule: str) -> (
        Tree, SubtreeProcessingResult):
    """
    Inserts needed article in given position

    :argument
    words_leaves -- list where article should be inserted

    :argument
    position -- position to insert in

    :argument
    article -- article to insert

    :argument
    rule -- cause, why insertion made

    :returns
    suggestions made for NP
    """
    start_ng = position
    end_ng = len(words_leaves)

    replacement_leaves = copy.deepcopy(words_leaves)
    if position == 0:
        replacement_leaves[0] = replacement_leaves[0].lower()
    replacement: str = f"{article} {' '.join(replacement_leaves[position:end_ng])}"

    suggestion = Suggestion(start_ng, end_ng, [replacement], rule)
    return SubtreeProcessingResult(words_leaves, [suggestion])


def resolve_np_group(pos_leaves: List[str],
                     words_leaves: List[str]) -> SubtreeProcessingResult:
    """
    Resolves where to place an article if NP was found by following grammar
    <CD>?<DT|PRP\$>?<JJS|JJ>*<NN|NNS>+

    :argument
    words_leaves -- see get_words_leaves()

    :argument
    pos_leaves -- see get_pos_leaves()

    :returns
    suggestions made for NP
    """
    if is_noun_plural(pos_leaves) or is_jj_superlative(pos_leaves) or has_unique_jj(
            words_leaves, pos_leaves):
        subtree_processing_result = insert_article_in_tree(0, 'the', words_leaves,
                                                           "Definite article because of plural form" if is_noun_plural(
                                                               pos_leaves) else "Definite article because of adjective")
    else:
        dt: str = resolve_vowel(words_leaves[0])
        subtree_processing_result = insert_article_in_tree(0, dt,
                                                           words_leaves, "Missed article before noun group")
        subtree_processing_resultThe = insert_article_in_tree(0, 'the',
                                                              words_leaves, "Missed article before noun group")
        subtree_processing_result.suggestions[0].replacements.append(
            subtree_processing_resultThe.suggestions[0].replacements[0]
        )
    return subtree_processing_result


def resolve_npp_group(pos_leaves: List[str],
                      words_leaves: List[str]) -> (
        Tree, Tree, SubtreeProcessingResult):
    """
    Resolves where to place an article if NP was found by following grammar
    <DT>+<NN>?<IN>?<CD>?<DT|PRP\$>?<JJS|JJ>*<NN|NNS>+

    :argument
    pos_leaves -- see get_pos_leaves()

    :argument
    words_leaves -- see get_words_leaves()

    :returns
    suggestions made for NP
    """
    if is_noun_plural(pos_leaves):
        subtree_processing_result = insert_article_in_tree(2, 'the',
                                                           words_leaves, "Definite article because of plural form")
    else:
        dt: str = resolve_vowel(words_leaves[2])
        subtree_processing_result = insert_article_in_tree(2, dt,
                                                           words_leaves, "Missed article before noun group")
        subtree_processing_resultThe = insert_article_in_tree(2, 'the',
                                                              words_leaves, "Missed article before noun group")
        subtree_processing_result.suggestions[0].replacements.append(
            subtree_processing_resultThe.suggestions[0].replacements[0]
        )
    return subtree_processing_result
