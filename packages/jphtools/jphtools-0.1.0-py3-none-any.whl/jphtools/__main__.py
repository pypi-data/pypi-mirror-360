import click
from jphtools.notebooks import strip_solutions_from_notebook

@click.group()
def cli():
    """jphtools: A collection of personal tools."""
    pass

@cli.group()
def notebook():
    """Notebook-related tools."""
    pass

@notebook.command("strip-answers")
@click.argument("input_path")
@click.argument("output_path")
def strip_answers(input_path, output_path):
    """Strip solution blocks from a Jupyter notebook."""
    strip_solutions_from_notebook(input_path, output_path)

if __name__ == "__main__":
    cli()
