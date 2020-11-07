import pytest
from hypothesis import given, settings, HealthCheck

from nbformat import reads
from nbformat.asynchronous import areads, avalidate, ValidationError

from . import strategies as nbs


@pytest.mark.asyncio
@given(nb_txt=nbs.a_valid_notebook_with_string())
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_areads_valid(nb_txt, caplog):
    nb, txt = nb_txt
    await areads(txt, nb.nbformat)
    assert "Notebook JSON" not in caplog.text


@pytest.mark.asyncio
@given(nb_txt=nbs.an_invalid_notebook_with_string())
@settings(suppress_health_check=[HealthCheck.too_slow])
async def test_areads_invalid(nb_txt, caplog):
    nb, txt = nb_txt
    await areads(txt, nb.nbformat)
    assert "Notebook JSON" in caplog.text
