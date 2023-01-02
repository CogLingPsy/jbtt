from typing import List, Tuple

import nltk
import nltk.tree
from nltk import Tree
from src.processing.models.Preloading import Preloading
from src.processing.models.Replace import Replace
from src.processing.utils.preprocessing_utils import fix_pos_tagging, prepare_sentence_for_tagging


def pos_tagging(phrase: str, preloading: Preloading) -> (List[Tuple[str, str]], List[Replace]):
    """
    Tags sentence with part-of-speech tags

    :argument
    phrase -- sentence to tag with POS-tags
    :argument
    preloading -- object containing dictionaries

    :returns
    list of tuples (word, tag) and list of replaces
    """
    tokens, replaces = prepare_sentence_for_tagging(phrase, preloading.contractions)
    tags: List[Tuple[str, str]] = nltk.pos_tag(tokens)
    fix_pos_tagging(tags, preloading.rules_fix_pos_tagging)

    # add tag IT, because there is need in grammar to differ pronouns between he-she and it
    same_word_tags: List[str] = ['it']
    tags: List[Tuple[str, str]] = [
        (w, w.upper()) if w in same_word_tags else (w, t)
        for w, t in tags
    ]

    # enrich with Named Entity tag
    entity_tags: Tree = nltk.ne_chunk(tags, binary=True)
    entity_index = []
    for chunk in entity_tags:
        if hasattr(chunk, 'label'):
            if not chunk[0]:  # nltk.ne_chunk counts every word with capital letter as NE, so that first word is excluded
                entity_index.append(entity_tags.index(chunk))
    if len(entity_index) != 0:
        for index in entity_index:
            tags[index] += ('NE',)
    return tags, replaces


def create_tree_from_grammar(tags: Tree) -> Tree:
    """
    Extracts noun groups according to grammar by Regexp rules

    :argument
    tags -- list of tuples (word, tag)

    :returns
    tree with indicated grammar groups
    """
    pattern: str = """
                EXIND: {<DT|EX|IT>+<VBZ|VBD>+<DT>?<JJ>*<NN>+}
                VBPART: {<VBZ|VBD><NN>+<IN>+}
                NPP: {<DT>+<NN>?<IN>?<CD>?<DT|PRP\$>?<JJS|JJ|JJR>*<NN|NNS>+}
                NP: {<CD>?<DT|PRP\$>?<JJS|JJ|JJR>*<NN|NNS>+}
                """
    cp: nltk.RegexpParser = nltk.RegexpParser(pattern)
    result: Tree = cp.parse(tags)

    # mark unmarked leafs with OTHER to process them further as trees and count symbols in them

    for index, element in enumerate(result):
        if not isinstance(element, Tree):
            if isinstance(element, Tuple):
                element = f"(OTHER {element[0]}/{element[1]})"
            result[index] = Tree.fromstring(str(element))
    tree: Tree = Tree.fromstring(str(result))

    return tree
