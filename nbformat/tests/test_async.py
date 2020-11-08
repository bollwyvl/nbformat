# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import io
import pytest
import contextlib
import tempfile
from pathlib import Path

import aiofiles
from hypothesis import given
from testfixtures import LogCapture

from ..constants import ENV_VAR_VALIDATOR, DEFAULT_ENCODING
from ..asynchronous import read, reads, write, writes, validate, ValidationError, NO_CONVERT
from ..json_compat import VALIDATORS

from . import strategies as nbs


@contextlib.contextmanager
def json_validator(validator_name):
    os.environ[ENV_VAR_VALIDATOR] = validator_name
    try:
        yield
    finally:
        os.environ.pop(ENV_VAR_VALIDATOR)



# some issues with setting environment variables mean they can just be parametrized
# pytest's caplog conflicts with hypothesis
async def _valid(nb, txt):
    """use the asynchronous API with a valid notebook, round-tripping to disk"""
    with LogCapture() as caplog:
        read_nb = await reads(txt, nb.nbformat)
        assert 'Notebook JSON' not in str(caplog)

        await validate(read_nb)

        with tempfile.TemporaryDirectory() as td:
            nb_path = os.path.join(td, 'notebook.ipynb')
            await write(read_nb, nb_path)
            await read(nb_path, nb['nbformat'])


async def _invalid(nb, txt):
    """use the asynchronous API with an invalid notebook, round-tripping to disk"""

    with LogCapture() as caplog:
        read_nb = await reads(txt, nb.nbformat)
        assert 'Notebook JSON' in str(caplog)

    with pytest.raises(ValidationError):
        await validate(read_nb)


@given(nb_txt=nbs.a_valid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_valid_default(nb_txt):
    with json_validator('jsonschema'):
        await _valid(*nb_txt)


@given(nb_txt=nbs.a_valid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_valid_fast(nb_txt):
    with json_validator('fastjsonschema'):
        await _valid(*nb_txt)


@given(nb_txt=nbs.an_invalid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_invalid_default(nb_txt):
    with json_validator('jsonschema'):
        await _invalid(*nb_txt)


@given(nb_txt=nbs.an_invalid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_invalid_fast(nb_txt):
    with json_validator('fastjsonschema'):
        await _invalid(*nb_txt)


@given(nb_txt=nbs.a_valid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_builtin_open(nb_txt):
    """someone's probably using `open`"""
    nb, txt = nb_txt
    with tempfile.TemporaryDirectory() as td:
        nb_path = Path(td) / 'notebook.ipynb'

        with open(nb_path, 'w+', encoding=DEFAULT_ENCODING) as fp:
            await write(nb, fp)

        with open(nb_path, 'r', encoding=DEFAULT_ENCODING) as fp:
            await read(fp, as_version=nb["nbformat"])


@given(nb_txt=nbs.a_valid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_like_jupyter_server(nb_txt):
    """ the atomic write stuff is rather complex, but it's basically `io.open`
    """
    nb, txt = nb_txt
    with tempfile.TemporaryDirectory() as td:
        nb_path = Path(td) / 'notebook.ipynb'

        # like _save_notebook[1]
        with io.open(nb_path, 'w+', encoding=DEFAULT_ENCODING) as fp:
            await write(nb, fp)

        # like _read_notebook[2]
        with io.open(nb_path, 'r', encoding=DEFAULT_ENCODING) as fp:
            await read(fp, as_version=nb["nbformat"])


"""
[1]: https://github.com/jupyter/jupyter_server/blob/1.0.5/jupyter_server/services/contents/fileio.py#L279-L282
[2]: https://github.com/jupyter/jupyter_server/blob/1.0.5/jupyter_server/services/contents/fileio.py#L254-L258
"""
