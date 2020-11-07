"""asynchronous API for nbformat"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import asyncio
import os
from pathlib import Path
import aiofiles

from . import reads, writes, read, write, validate, NO_CONVERT, ValidationError
from .constants import DEFAULT_ENCODING

def _loop():
    return asyncio.get_event_loop()


# shim calls for tracing, etc.
def _reads(s, as_version, kwargs_):
    return reads(s, as_version, **kwargs_)


def _writes(nb, version, kwargs_):
    return writes(nb, version, **kwargs_)


def _validate(nbdict, ref, version, version_minor, relax_add_props, nbjson):
    return validate(nbdict, ref, version, version_minor, relax_add_props, nbjson)


__all__ = [
    'NO_CONVERT',
    'DEFAULT_ENCODING',
    'ValidationError',
    # asynchronous API
    'areads',
    'aread',
    'awrites',
    'awrite',
    'avalidate'
]


async def areads(s, as_version, **kwargs):
    return await _loop().run_in_executor(None, _reads, s, as_version, kwargs)


async def aread(fp, as_version, **kwargs):
    async with aiofiles.open(fp, encoding=DEFAULT_ENCODING) as afp:
        return await areads(await afp.read(), as_version, **kwargs)


async def awrites(nb, version=NO_CONVERT, **kwargs):
    return await _loop().run_in_executor(None, _writes, nb, version, kwargs)


async def awrite(nb, fp, version=NO_CONVERT, **kwargs):
    nb_str = await awrites(nb, version, **kwargs)
    async with aiofiles.open(fp, 'w+', encoding=DEFAULT_ENCODING) as afp:
        await afp.write(nb_str)


async def avalidate(nbdict=None, ref=None, version=None, version_minor=None,
                    relax_add_props=False, nbjson=None):
    return await _loop().run_in_executor(None, _validate, nbdict, ref, version,
                                         version_minor, relax_add_props, nbjson)
