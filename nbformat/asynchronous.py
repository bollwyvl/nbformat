"""asynchronous API for nbformat"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import asyncio
import os
import io
from pathlib import Path
import aiofiles
from aiofiles.threadpool.text import AsyncTextIOWrapper

from . import (
    NO_CONVERT, ValidationError,
    reads as reads_sync, writes as writes_sync, validate as validate_sync
)
from .constants import DEFAULT_ENCODING

AIOFILES_OPENABLE = (str, bytes, os.PathLike)


def _loop():
    """get the current event loop
       this may need some more work later
    """
    return asyncio.get_event_loop()


# shim calls for tracing, etc.
def _reads(s, as_version, kwargs_):
    return reads_sync(s, as_version, **kwargs_)


def _writes(nb, version, kwargs_):
    return writes_sync(nb, version, **kwargs_)


def _validate(nbdict, ref, version, version_minor, relax_add_props, nbjson):
    return validate_sync(nbdict, ref, version, version_minor, relax_add_props, nbjson)


__all__ = [
    'NO_CONVERT',
    'DEFAULT_ENCODING',
    'ValidationError',
    # asynchronous API
    'reads',
    'read',
    'writes',
    'write',
    'validate'
]


async def reads(s, as_version, **kwargs):
    return await _loop().run_in_executor(None, _reads, s, as_version, kwargs)


async def writes(nb, version=NO_CONVERT, **kwargs):
    return await _loop().run_in_executor(None, _writes, nb, version, kwargs)


async def read(fp, as_version, **kwargs):
    if isinstance(fp, AIOFILES_OPENABLE):
        async with aiofiles.open(fp, encoding=DEFAULT_ENCODING) as afp:
            nb_str = await afp.read()
    elif isinstance(fp, io.TextIOWrapper):
        nb_str = await AsyncTextIOWrapper(fp, loop=_loop(), executor=None).read()
    else:
        raise NotImplementedError(f"Don't know how to read {type(fp)}")

    return await reads(nb_str, as_version, **kwargs)


async def write(nb, fp, version=NO_CONVERT, **kwargs):
    nb_str = await writes(nb, version, **kwargs)

    if isinstance(fp, AIOFILES_OPENABLE):
        async with aiofiles.open(fp, 'w+', encoding=DEFAULT_ENCODING) as afp:
            return await afp.write(nb_str)
    elif isinstance(fp, io.TextIOWrapper):
        return await AsyncTextIOWrapper(fp, loop=_loop(), executor=None).write(nb_str)
    else:
        raise NotImplementedError(f"Don't know how to write {type(fp)}")


async def validate(nbdict=None, ref=None, version=None, version_minor=None,
                    relax_add_props=False, nbjson=None):
    return await _loop().run_in_executor(None, _validate, nbdict, ref, version,
                                         version_minor, relax_add_props, nbjson)
