from reactpy.types import ComponentType, VdomDict
from typing import Callable, Awaitable
from reactpy import component, hooks
from functools import wraps
import asyncio

def Rebound(fallback: ComponentType, requestfn: Callable[..., Awaitable]) -> Callable[[ComponentType], ComponentType]:
    """
    A decorator that renders a fallback component while the request is loading.
    """
    def decorator(_component: ComponentType) -> ComponentType:
        @wraps(_component)
        @component
        def wrapper(*args, **kwargs):
            res, set_res = hooks.use_state(None)

            async def fetch():
                while True:
                    response = await requestfn(*args, **kwargs)
                    if response is not None:
                        set_res(response)
                        break
                    await asyncio.sleep(0.1)

            hooks.use_effect(lambda: asyncio.create_task(fetch()), [])

            if res is None:
                return fallback(*args, **kwargs) if isinstance(fallback, Callable) else fallback
            else:
                return _component(res, *args, **kwargs)

        return wrapper
    return decorator

@component
def inRebound(_component : ComponentType | VdomDict, fallback: ComponentType | VdomDict, requestfn: Callable[..., Awaitable]) -> VdomDict | ComponentType:
    """
    Rebound but for inside of a component.
    """
    res, set_res = hooks.use_state(None)

    async def fetch():
        while True:
            response = await requestfn()
            if response is not None:
                set_res(response)
                break
            await asyncio.sleep(0.1)

    hooks.use_effect(lambda: asyncio.create_task(fetch()), [])

    if res is None:
        return fallback() if isinstance(fallback, Callable) else fallback
    else:
        return _component(res)