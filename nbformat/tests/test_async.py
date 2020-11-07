import os
import pytest
import contextlib
from hypothesis import given

from nbformat.asynchronous import aread, areads, awrite, awrites, avalidate, ValidationError
from nbformat.json_compat import VALIDATORS
import tempfile

from . import strategies as nbs


@contextlib.contextmanager
def json_validator(validator_name):
    os.environ["NBFORMAT_VALIDATOR"] = validator_name
    try:
        yield
    finally:
        os.environ.pop("NBFORMAT_VALIDATOR")



# some issues with setting the environment mean they can just be parametrized
async def _valid(nb_txt, caplog):
    nb, txt = nb_txt
    read_nb = await areads(txt, nb.nbformat)
    assert "Notebook JSON" not in caplog.text

    await avalidate(read_nb)

    with tempfile.TemporaryDirectory() as td:
        nb_path = os.path.join(td, "notebook.ipynb")
        await awrite(read_nb, nb_path)
        await aread(nb_path, nb["nbformat"])

@given(nb_txt=nbs.a_valid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_valid_default(nb_txt, caplog):
    with json_validator("jsonschema"):
        await _valid(nb_txt, caplog)


@given(nb_txt=nbs.a_valid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_valid_fast(nb_txt, caplog):
    with json_validator("fastjsonschema"):
        await _valid(nb_txt, caplog)


async def _invalid(nb_txt, caplog):
    nb, txt = nb_txt
    read_nb = await areads(txt, nb.nbformat)
    assert "Notebook JSON" in caplog.text

    with pytest.raises(ValidationError):
        await avalidate(read_nb)


@given(nb_txt=nbs.an_invalid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_invalid_default(nb_txt, caplog):
    with json_validator("jsonschema"):
        await _invalid(nb_txt, caplog)


@given(nb_txt=nbs.an_invalid_notebook_with_string())
@nbs.base_settings
@pytest.mark.asyncio
async def test_async_invalid_false(nb_txt, caplog):
    with json_validator("fastjsonschema"):
        await _invalid(nb_txt, caplog)
