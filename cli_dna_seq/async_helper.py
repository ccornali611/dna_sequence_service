import asyncio
from typing import Any, Callable, TypeVar

_Func = TypeVar('_Func', bound=Callable[..., Any])

def make_async_call(func: _Func, loop: asyncio.AbstractEventLoop):
    return loop.run_until_complete(async_wapper(func))

async def async_wapper(func):
    try:
        return await func
    except Exception as error:
        return error
