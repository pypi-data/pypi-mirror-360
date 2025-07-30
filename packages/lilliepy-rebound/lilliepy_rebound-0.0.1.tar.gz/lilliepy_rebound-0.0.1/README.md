# lilliepy-rebound
suspense tag but for react py

## Usage:
two ways to use rebounds:
* ``` Rebound(fallback: ComponentType, requestfn: Callable[..., Awaitable]) -> Callable[[ComponentType], ComponentType] ```
* ``` inRebound(_component : ComponentType | VdomDict, fallback: ComponentType | VdomDict, requestfn: Callable[..., Awaitable]) -> VdomDict | ComponentType ```

### @Rebound()
This is the way to use the decorator version of Rebounding
```py
from reactpy import component, html, run
from lilliepy_rebound import Rebound
from requests import get

async def get_data():
   #expensive request
   return get("http://127.0.0.1:5000/hello").json()

@component
@Rebound(fallback=html.h1("Loading..."), requestfn=get_data)
def MyComponent(data):
    return html._(
            html.h1(f"{data}")
        )

run(MyComponent)
```

the Rebound functions gives a param ``` res ``` to the component it is attached to. ``` res ``` contains the data received when the request is complete

### inRebound()
This is the way to use the component version of Rebounding
```py
from reactpy import component, html, run
from lilliepy_rebound import Rebound, inRebound
from requests import get

async def get_data():
   #expensive request
   return get("http://127.0.0.1:5000/hello").json()

@component
def MyComponent():
    return html._(
            inRebound(lambda data: html.div(f"Result: {data['data']}"), html.div("Loading..."), get_data)
        )

run(MyComponent)
```

basically the same thing as Rebound but it is a component instead of a decorator