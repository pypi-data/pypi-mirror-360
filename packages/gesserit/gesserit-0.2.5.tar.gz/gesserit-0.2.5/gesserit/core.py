import asyncio
import importlib.resources as resources
import inspect
import json
from functools import partial
from typing import Any, Callable, Coroutine, Optional, Union

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

templates = Jinja2Templates(directory=str(resources.files(__package__) / "templates"))


class SearchItem(BaseModel):
    text: str
    metadata: Optional[dict[str, Any]] = None


class ParameterInfo(BaseModel):
    name: str
    type: type
    default: Any = None


class Gesserit:
    def __init__(
        self,
        search_function: Union[Callable[..., list[SearchItem]], Callable[..., Coroutine[Any, Any, list[SearchItem]]]],
    ):
        self.app = FastAPI()
        templates.env.globals["url_for"] = self.app.url_path_for
        self.app.mount("/static", StaticFiles(directory="gesserit/static"), name="static")

        self.search_function = search_function
        self.parameters = self._inspect_handler_parameters()

        self.app.add_api_route(
            "/", partial(root, parameters=self.parameters), response_class=HTMLResponse, methods=["GET"], name="root"
        )
        self.app.add_api_route(
            "/search",
            partial(search, search_function=self.search_function, parameters=self.parameters),
            response_class=HTMLResponse,
            methods=["POST"],
            name="search",
        )

    def _inspect_handler_parameters(self) -> list[ParameterInfo]:
        """Inspect the handler function to extract parameter information."""
        sig = inspect.signature(self.search_function)
        parameters = []

        for param_name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            if param_type not in (str, bool, float, int):
                param_type = str
            default = param.default if param.default != inspect.Parameter.empty else None
            parameters.append(ParameterInfo(name=param_name, type=param_type, default=default))
        return parameters

    def run(self, **kwargs):
        """Run the Gesserit server.

        Args:
            **kwargs: Additional arguments to pass to the uvicorn.run function.
        """
        uvicorn.run(self.app, **kwargs)


async def root(request: Request, parameters: list[ParameterInfo]) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "search_results": [],
            "parameters": parameters,
        },
    )


async def search(
    request: Request,
    search_function: Union[Callable[..., list[SearchItem]], Callable[..., Coroutine[Any, Any, list[SearchItem]]]],
    parameters: list[ParameterInfo],
    query_param: str = Form(...),
) -> HTMLResponse:
    query_data = json.loads(query_param)
    if asyncio.iscoroutinefunction(search_function):
        search_results = await search_function(**query_data)
    else:
        search_results = search_function(**query_data)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "search_results": search_results,
            "parameters": parameters,
        },
    )
