# This script will strip sections of cells between
# '# BEGIN_SOLUTION' & '# END_SOLUTION' and
# replace it with '# ADD YOUR CODE HERE'
# to produce student-friendly versions of Jupyter notebooks
import nbformat
import re
import argparse


def strip_solutions_from_notebook(input_path, output_path):
    """
    Removes solution blocks from a Jupyter notebook and writes the result to output_path.
    Solution blocks are marked by '# BEGIN_SOLUTION' and '# END_SOLUTION'.
    """
    with open(input_path, "r") as f:
        nb = nbformat.read(f, as_version=4)

    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.source = re.sub(
                r"# BEGIN_SOLUTION.*?# END_SOLUTION",
                "# ADD YOUR CODE HERE",
                cell.source,
                flags=re.DOTALL,
            )

    with open(output_path, "w") as f:
        nbformat.write(nb, f)


def main():
    parser = argparse.ArgumentParser(
        description="Strip solution blocks from a Jupyter notebook."
    )
    parser.add_argument(
        "input_path", help="Path to the input notebook (with solutions)"
    )
    parser.add_argument(
        "output_path", help="Path to the output notebook (student version)"
    )
    args = parser.parse_args()
    strip_solutions_from_notebook(args.input_path, args.output_path)


if __name__ == "__main__":
    main()
