"""asynchronous API for nbformat"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import asyncio
import os
from pathlib import Path
import aiofiles

from . import (
    NO_CONVERT, ValidationError,
    reads as reads_sync, writes as writes_sync, validate as validate_sync
)
from .constants import DEFAULT_ENCODING

def _loop():
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


async def read(fp, as_version, **kwargs):
    async with aiofiles.open(fp, encoding=DEFAULT_ENCODING) as afp:
        return await reads(await afp.read(), as_version, **kwargs)


async def writes(nb, version=NO_CONVERT, **kwargs):
    return await _loop().run_in_executor(None, _writes, nb, version, kwargs)


async def write(nb, fp, version=NO_CONVERT, **kwargs):
    nb_str = await writes(nb, version, **kwargs)
    async with aiofiles.open(fp, 'w+', encoding=DEFAULT_ENCODING) as afp:
        await afp.write(nb_str)


async def validate(nbdict=None, ref=None, version=None, version_minor=None,
                    relax_add_props=False, nbjson=None):
    return await _loop().run_in_executor(None, _validate, nbdict, ref, version,
                                         version_minor, relax_add_props, nbjson)
