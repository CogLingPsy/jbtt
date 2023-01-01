from typing import List

import nltk
from src.processing.models.Replace import Replace
from src.processing.checkers import is_noun_uncountable, is_determinative_in_group, resolve_vowel, \
    is_named_entity, is_a_group_of, is_quantity_of
from src.processing.models.SubtreeProcessingResult import SubtreeProcessingResult
from src.processing.models.dtos import SentenceDto
from src.processing.utils.tree_processing_utils import get_words_leaves, get_pos_leaves, insert_article_in_tree, \
    resolve_npp_group, resolve_np_group


def process_tree(phrase, tree: nltk.Tree, replaces: List[Replace], uncountable_nouns_list: List[str]) -> SentenceDto:
    """
    The core process
    Resolves whether to insert article in NP

    :argument
    tree -- tree of sentence with extracted NPs by grammar
    :argument
    replaces -- list of replaces to fix sentence to the initial state
    :argument
    uncountable_nouns_list -- list containing uncountable nouns

    :returns
    suggestion containing NP with article and positions of start and end of NP
    """

    def empty_suggestion():
        tree_processing_result.concat(SubtreeProcessingResult(words_leaves, []))

    tree_processing_result = SubtreeProcessingResult([], [])
    for subtree in tree.subtrees(lambda t: t.height() == 2):

        words_leaves: List[str] = get_words_leaves(subtree.leaves())
        pos_leaves: List[str] = get_pos_leaves(subtree.leaves())

        if subtree.label() == 'EXIND':
            if pos_leaves[2] == 'DT':
                empty_suggestion()
            else:
                if is_named_entity(subtree.leaves()):
                    empty_suggestion()
                dt: str = resolve_vowel(words_leaves[2])
                tree_processing_result.concat(
                    insert_article_in_tree(2, dt, words_leaves, "Indefinite article after It is, There is, etc."))
        elif subtree.label() == 'VBPART':
            empty_suggestion()

        elif subtree.label() == 'NPP':
            if is_noun_uncountable(subtree, uncountable_nouns_list) or is_named_entity(
                    subtree.leaves()) or is_a_group_of(words_leaves):
                empty_suggestion()
            if is_quantity_of(words_leaves):
                tree_processing_result.concat(insert_article_in_tree(2, "the", words_leaves,
                                                                     "Constructions of type 'All of', 'None of' with definite article"))
            else:
                if is_determinative_in_group(pos_leaves):
                    empty_suggestion()
                else:
                    tree_processing_result.concat(resolve_npp_group(pos_leaves, words_leaves))

        elif subtree.label() == 'NP':
            if is_noun_uncountable(subtree, uncountable_nouns_list) or is_determinative_in_group(
                    pos_leaves) or is_named_entity(subtree.leaves()):
                empty_suggestion()
            else:
                tree_processing_result.concat(resolve_np_group(pos_leaves, words_leaves))

        else:
            empty_suggestion()

    for replace in reversed(replaces):
        tree_processing_result.apply_replace(replace)

    result = tree_processing_result.get_sentence(phrase)
    return result
