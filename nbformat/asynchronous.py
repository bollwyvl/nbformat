""" experimental asynchronous API for nbformat
"""
import asyncio
import os
from pathlib import Path
import aiofiles

from . import reads, writes, read, write, validate, NO_CONVERT, ValidationError

def _loop():
    return asyncio.get_running_loop()


# shim calls for tracing, etc.
def _reads(s, as_version, kwargs_):
    return reads(s, as_version, **kwargs_)


def _read(fp, as_version, kwargs_):
    return read(fp, as_version, **kwargs_)


def _writes(nb, version, kwargs_):
    return writes(nb, version, **kwargs_)


def _write(nb, fp, version, kwargs_):
    return writes(nb, fp, version, **kwargs_)

def _validate(nbdict, ref, version, version_minor, relax_add_props, nbjson):
    return validate(nbdict, ref, version, version_minor, relax_add_props, nbjson)


__all__ = [
    "NO_CONVERT",
    # synchronous API
    "reads",
    "read",
    "writes",
    "write",
    "validate",
    # asynchronous API
    "areads",
    "aread",
    "awrites",
    "awrite",
    "avalidate"
]


async def areads(s, as_version, **kwargs):
    return await _loop().run_in_executor(None, _reads, s, as_version, kwargs)


async def aread(fp, as_version, **kwargs):
    with aiofiles.open(fp) as afp:
        return await areads(await afp.read(), as_version, **kwargs)

    return await _loop().run_in_executor(None, _read, fp, as_version, kwargs)


async def awrites(nb, version=NO_CONVERT, **kwargs):
    return await _loop().run_in_executor(None, _writes, nb, version, kwargs)


async def awrite(nb, fp, version=NO_CONVERT, **kwargs):
    if isinstance(fp, str):
        with aiofiles.open(fp, "w+") as afp:
            return await awrites(nb, await afp.read(), version, **kwargs)
    elif isinstance(fp, Path):
        with aiofiles.open(str(fp), "w+") as afp:
            return await awrites(nb, await afp.read(), version, **kwargs)

    return await _loop().run_in_executor(None, _write, nb, fp, version, kwargs)


async def avalidate(nbdict=None, ref=None, version=None, version_minor=None,
                    relax_add_props=False, nbjson=None):
    return await _loop().run_in_executor(None, _validate, nbdict, ref, version,
                                         version_minor, relax_add_props, nbjson)
