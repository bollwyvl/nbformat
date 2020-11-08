# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import pytest
import contextlib
import tempfile

from hypothesis import given

from ..constants import ENV_VAR_VALIDATOR
from ..asynchronous import read, reads, write, writes, validate, ValidationError
from ..json_compat import VALIDATORS

from . import strategies as nbs
from testfixtures import LogCapture


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
