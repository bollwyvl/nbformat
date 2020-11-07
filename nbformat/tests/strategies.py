"""nbformat strategies for hypothesis"""
import pytest
import re
from pathlib import Path
from hypothesis import given, strategies as st, assume, settings, HealthCheck

from nbformat import validate, reads, writes
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).parent
ALL_NOTEBOOK_TEXT = [p.read_text(encoding="utf-8") for p in HERE.glob("*.ipynb")]
ALL_NOTEBOOKS = [
    reads(nb_text, int(re.findall(r"""nbformat":\s+(\d+)""", nb_text)[0]))
    for nb_text in ALL_NOTEBOOK_TEXT
]

def _is_valid(nb):
    try:
        validate(nb)
        return True
    except:
        return False

VALID_NOTEBOOKS = [nb for nb in ALL_NOTEBOOKS if _is_valid(nb)]
INVALID_NOTEBOOKS = [nb for nb in ALL_NOTEBOOKS if nb not in VALID_NOTEBOOKS]

CELL_TYPES = [new_code_cell, new_markdown_cell]
# , nbformat.new_text_cell, nbformat.new_notebook_cell]

# Most tests will need this decorator, because fileio and threads are slow
base_settings = settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)

a_cell_generator = st.sampled_from(CELL_TYPES)
a_test_notebook = st.sampled_from(ALL_NOTEBOOKS)
a_valid_test_notebook = st.sampled_from(VALID_NOTEBOOKS)
an_invalid_test_notebook = st.sampled_from(INVALID_NOTEBOOKS)


@st.composite
def a_cell(draw):
    Cell = draw(a_cell_generator)
    cell = Cell()
    cell.source = draw(st.text())
    return cell


@st.composite
def a_new_notebook(draw):
    notebook = new_notebook()
    cell_count = draw(st.integers(min_value=1, max_value=100))
    notebook.cells = [draw(a_cell()) for i in range(cell_count)]

    return notebook


@st.composite
def a_valid_notebook(draw):
    if draw(st.booleans()):
        return draw(a_valid_test_notebook)

    return draw(a_new_notebook())


@st.composite
def an_invalid_notebook(draw):
    # TODO: some mutations to make a valid notebook invalid
    return draw(an_invalid_test_notebook)


@st.composite
def a_valid_notebook_with_string(draw):
    notebook = draw(a_valid_notebook())
    return notebook, writes(notebook)


@st.composite
def an_invalid_notebook_with_string(draw):
    notebook = draw(an_invalid_notebook())
    return notebook, writes(notebook)
