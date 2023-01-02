import os
import sys
from typing import IO

import click

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
grandparent = os.path.dirname(parent)
sys.path.append(grandparent)

from src.processing.run_processing import process_text


@click.command()
@click.option('--text', help='')
@click.option('--input_file', type=click.File('r', encoding='utf-8'))
def cli_text(text: str, input_file: IO):
    """
    Cli app to run processing from terminal
    python src/applications/cli.py --text="It’s beautiful city. He is actor."
    python src/applications/cli.py --input_file=resources/moby_dick
    """
    if input_file:
        text: str = input_file.read()
    answer = process_text(text, True)

    for results in answer:
        sentence = results['text']
        if not results['suggestions']:
            if sentence.strip() != "":
                click.secho(f"Sentence '{sentence}' is completely fine!", fg='green')
        else:
            click.secho(f"Can suggest improvements for '{sentence}'", fg='blue')
            for suggestion in results['suggestions']:
                click.secho(f"Cause: '{suggestion['cause']}'", fg='blue')
                click.secho(sentence[0:suggestion['start']], nl=False)
                click.secho(sentence[suggestion['start']:suggestion['end']], fg='red', nl=False)
                click.secho(sentence[suggestion['end']:-1])
                click.secho(f"Suggestions: ", nl=False)
                click.secho("; ".join(suggestion['replacements']), fg='green')
            click.echo('\n')


if __name__ == '__main__':
    cli_text()
