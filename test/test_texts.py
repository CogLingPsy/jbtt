import json
import os
import sys
from typing import List

import allure
import pytest
from click.testing import CliRunner
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from src.applications.app import app
from src.applications.cli import cli_text
from src.processing.models.dtos import SentenceDto, SuggestionDto
from src.processing.models.Preloading import Preloading
from src.processing.run_processing import process_sentence, process_text
from src.processing.utils.load_utils import download_nltk_modules, load_dictionaries


@pytest.mark.parametrize("sentence, result",
                         [
                             ('It’s beautiful city',
                              [SuggestionDto(start=5, end=19, cause='Indefinite article after It is, There is, etc.',
                                             replacements=['a beautiful city'])]),
                             ('There are two cats', [])
                         ])
@allure.feature("Grammar")
@allure.story("After copula")
@allure.title("Constructions of type 'This is', 'It is', 'There is' with indefinite article")
def test_to_be_constructions(init_dictionaries, sentence, result):
    allure_params_step(sentence, result)
    text: SentenceDto = run_processing(init_dictionaries, sentence)
    check_assertion(text['suggestions'], result)


@pytest.mark.parametrize("sentence, result",
                         [
                             ('He is actor.',
                              [SuggestionDto(start=6, end=12, cause='Missed article before noun group',
                                             replacements=['an actor', 'the actor'])]),
                             ('She is beautiful', [])
                         ])
@allure.feature("Grammar")
@allure.story("After copula")
@allure.title("Constructions of type 'is a/the profession'")
def test_before_profession(init_dictionaries, sentence, result):
    allure_params_step(sentence, result)
    text: SentenceDto = run_processing(init_dictionaries, sentence)
    check_assertion(text['suggestions'], result)


@pytest.mark.parametrize("sentence, result",
                         [
                             ('Let’s look at int array closer',
                              [SuggestionDto(start=14, end=23, cause='Missed article before noun group',
                                             replacements=['an int array', 'the int array'])]),
                             ('Cats played with cat toys',
                              [SuggestionDto(start=0, end=4, cause='Definite article because of plural form',
                                             replacements=['the cats']),
                               SuggestionDto(start=17, end=25, cause='Definite article because of plural form',
                                             replacements=['the cat toys'])
                               ])])
@allure.feature("Grammar")
@allure.story("Collocations")
@allure.title("Constructions of type 'noun as adjective for noun'")
def test_noun_with_prenoun(init_dictionaries, sentence, result):
    allure_params_step(sentence, result)
    text: SentenceDto = run_processing(init_dictionaries, sentence)
    check_assertion(text['suggestions'], result)


@pytest.mark.parametrize("sentence, result",
                         [
                             ('Boy came to me',
                              [SuggestionDto(start=0, end=3, cause='Missed article before noun group',
                                             replacements=['a boy', 'the boy'])]),
                             ('The cat was sitting on the table', [])
                         ])
@allure.feature("Grammar")
@allure.title("Article for subject")
def test_subject(init_dictionaries, sentence, result):
    allure_params_step(sentence, result)
    text: SentenceDto = run_processing(init_dictionaries, sentence)
    check_assertion(text['suggestions'], result)


@pytest.mark.parametrize("sentence, result",
                         [
                             ('All of students were present.',
                              [SuggestionDto(start=7, end=15,
                                             cause="Constructions of type 'All of', 'None of' with definite article",
                                             replacements=['the students'])]),
                             ('A part of students were present.', [])
                         ])
@allure.feature("Grammar")
@allure.story("Collocations")
@allure.title("Constructions of type 'All of', 'None of' with definite article")
def test_quantity_of_collocations(init_dictionaries, sentence, result):
    allure_params_step(sentence, result)
    text: SentenceDto = run_processing(init_dictionaries, sentence)
    check_assertion(text['suggestions'], result)


@pytest.mark.parametrize("sentence, result",
                         [
                             ('Main part is fantastic.',
                              [SuggestionDto(start=0, end=9,
                                             cause='Definite article because of adjective',
                                             replacements=['the main part'])]),
                             ('Magical part is fantastic.',
                              [SuggestionDto(start=0, end=12,
                                             cause='Missed article before noun group',
                                             replacements=['a magical part', 'the magical part'])])
                         ])
@allure.feature("Grammar")
@allure.story("Adjectives")
@allure.title("Constructions of type 'The main', 'The same' with definite article")
def test_unique_adjective(init_dictionaries, sentence, result):
    allure_params_step(sentence, result)
    text: SentenceDto = run_processing(init_dictionaries, sentence)
    check_assertion(text['suggestions'], result)


@pytest.mark.parametrize("sentence, result",
                         [
                             ('In greatest city in world',
                              [SuggestionDto(start=3, end=16,
                                             cause='Definite article because of adjective',
                                             replacements=['the greatest city']),
                               SuggestionDto(start=20, end=25,
                                             cause='Missed article before noun group',
                                             replacements=['a world', 'the world'])
                               ]),
                             ('In great city in the world',
                              [SuggestionDto(start=3, end=13,
                                             cause='Missed article before noun group',
                                             replacements=['a great city', 'the great city'])])])
@allure.feature("Grammar")
@allure.story("Adjectives")
@allure.title("Definite article with superlative adjective")
def test_superlative(init_dictionaries, sentence, result):
    allure_params_step(sentence, result)
    text: SentenceDto = run_processing(init_dictionaries, sentence)
    check_assertion(text['suggestions'], result)


@pytest.mark.parametrize("sentence, result",
                         [
                             ('I like this actor', []),
                             ('I’ve seen my favourite actor today!', []),
                             ('Time is money', []),
                             ('He was part of a group of students', [])
                         ])
@allure.feature("Grammar")
@allure.story("No article")
@allure.title("Constructions with no articles to add")
def test_negative(init_dictionaries, sentence, result):
    allure_params_step(sentence, result)
    text: SentenceDto = run_processing(init_dictionaries, sentence)
    check_assertion(text['suggestions'], result)


@allure.feature("Application")
@allure.story("CLI")
@allure.title("Cli prints output")
def test_cli():
    text = "It’s beautiful city. He is actor. Let’s look at int array closer. Boy came to me. All of students were " \
           "present. Main part is fantastic. In greatest city in the world. I like this actor. I’ve seen my favourite " \
           "actor today! Time is money. He was part of a group of students "
    with allure.step(f"Run cli for {text.split('.')[0] + '...'}"):
        allure.attach(body=text, name='Text to process', attachment_type=allure.attachment_type.TEXT)
        runner = CliRunner()
        result = runner.invoke(cli_text, [f'--text="{text}"'])

    with allure.step("Exit code 0, output contains values"):
        assert result.exit_code == 0
        assert 'It’s beautiful city.' in result.stdout
        assert "Sentence 'I like this actor.' is completely fine!" in result.stdout


@allure.feature("Application")
@allure.story("API")
@allure.title("Post to local server")
def test_server():
    with allure.step(f"Run test API client"):
        client = app.test_client()
    with allure.step(f"Execute POST request"):
        request_text = {"text": "It’s beautiful city. He is actor."}
        response = client.post('/processText',
                               json=request_text)
        allure.attach(body=json.dumps(request_text), name='Text to process',
                      attachment_type=allure.attachment_type.JSON)
    with allure.step(f"Response code == 200, response body as expected"):
        assert response.status_code == 200
        expected_response = [
            SentenceDto(text='It’s beautiful city.', suggestions=[
                SuggestionDto(start=5, end=20, cause='Indefinite article after It is, There is, etc.',
                              replacements=['a beautiful city'])]),
            SentenceDto(text='He is actor.',
                        suggestions=[SuggestionDto(start=6, end=12, cause='Missed article before noun group',
                                                   replacements=['an actor', 'the actor'])])
        ]
        assert response.json == expected_response
        allure.attach(body=json.dumps(expected_response), name='Expected response',
                      attachment_type=allure.attachment_type.JSON)
        allure.attach(body=json.dumps(response.json), name='Actual response',
                      attachment_type=allure.attachment_type.JSON)


@allure.feature("Application")
@allure.story("Cache")
@allure.title("Number of additional suggestions")
def test_big_text_quality(load_moby_dick):
    with allure.step(f"Run process_text for resources/moby_dick"):
        answer: List[SentenceDto] = process_text(load_moby_dick, True)
    with allure.step("Number of suggestions"):
        assert len([item for item in answer if
                    item['suggestions'] != []]) < 15000, "Too many suggestions for initially right corrected text"


@pytest.mark.timeout(5)
#Fails if run out of timeout
@allure.feature("Application")
@allure.story("Cache")
@allure.title("Process time")
def test_big_text(load_moby_dick):
    with allure.step(f"Run process_text for resources/moby_dick"):
        process_text(load_moby_dick, True)


@allure.step("Parametrize step")
def allure_params_step(sentence, result):
    pass


@allure.step("Run processing of articles' insertion")
def run_processing(init_dictionaries, text):
    return process_sentence(text, init_dictionaries)


@allure.step("Check insertion is relevant")
def check_assertion(actual, expected):
    assert actual == expected


@pytest.fixture(scope='session', autouse=True)
def init_dictionaries():
    with allure.step("Load dictionaries"):
        modules_updated: bool = download_nltk_modules()
        contractions, rules_fix_pos_tagging, uncountable_nouns_list = load_dictionaries()
    return Preloading(contractions, rules_fix_pos_tagging, uncountable_nouns_list, modules_updated)


@pytest.fixture(scope='function')
def load_moby_dick():
    with allure.step("Get Moby-Dick from Gutenberg"):
        filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources/moby_dick')
        if not os.path.exists(filepath):
            text = strip_headers(load_etext(2701)).strip()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
    with allure.step("Cache exists"):
        hashes_json = os.path.join(os.path.dirname(__file__), "../../resources/dictionaries/hashes.json")
        if os.path.exists(hashes_json):
            return text
        else:
            process_text(text, True)
            return text
