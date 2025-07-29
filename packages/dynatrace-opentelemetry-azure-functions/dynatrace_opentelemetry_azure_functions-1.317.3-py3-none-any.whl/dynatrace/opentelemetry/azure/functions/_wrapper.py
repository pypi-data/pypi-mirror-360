# Copyright 2022 Dynatrace LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import inspect
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

import wrapt
from azure import functions as func

from dynatrace.opentelemetry.azure.functions._bindings import KW_CONTEXT
from dynatrace.opentelemetry.azure.functions._triggers import determine_trigger

_SAFE_REPR_TYPES = (bool, type(None), int, str)
HandlerT = TypeVar("HandlerT", bound=Callable[..., Any])


def wrap_handler(
    handler: HandlerT = None,
    http_result_param_name: Optional[str] = None,
) -> HandlerT:
    """A decorator for tracing Azure Function invocations.

    The decorator wraps the given function handler and creates spans for every
    invocation. It can be used for normal and 'async' handler functions.

    Example usage::

        @wrap_handler
        def handler(req: HttpRequest) -> HttpResponse
            # do something
            return HttpResponse("Hello World", status_code=200)

    HTTP handler functions that do not return an explicit result but instead use
    multiple 'Out' bindings should provide the name of the result binding as binding
    hint to decorator's 'http_result_param_name' parameter.
    See the following HTTP function for example::

        @wrap_handler(http_result_param_name="res")
        def handler(req: HttpRequest, res: Out, other: Out):
            # do something
            res.set(HttpResponse("Hello World"), status_code=200)

    The `context <https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python#context>`_
    is a special parameter that is dynamically passed to the Azure Function by the
    runtime if it is in the handler's signature.
    The decorator/wrapper transparently adds it to its signature if it is not in
    the handler's signature for the purpose of extracting relevant span attributes.
    Make sure not to use the name 'context' for any binding in your 'function.json`
    as this would shadow the context object and certain span attributes cannot.
    be extracted. Adding the context to the handler's signature doesn't pose a
    problem as shown in the following example::

        @wrap_handler
        def handler(req: HttpRequest, context: Context) -> str:
            return "Hello World"

    Args:
        handler: the Azure Function handler to wrap.
        http_result_param_name: a biding hint to determine the result of an HTTP
            triggered function when having no explicit return value and multiple
            'Out' bindings.
    """
    if handler is None:
        return functools.partial(
            wrap_handler, http_result_param_name=http_result_param_name
        )

    if not callable(handler):
        raise ValueError(
            f"'handler': expected callable but got '{type(handler)}'"
        )

    sig = inspect.signature(handler)
    is_async = inspect.iscoroutinefunction(handler)
    has_context = KW_CONTEXT in sig.parameters
    adapter = None
    if not has_context:
        adapter = _make_wrapper_adapter(sig, is_async)

    if is_async:

        @wrapt.decorator(adapter=adapter)
        async def _async_wrapper(wrapped, instance, args, kwargs):
            trigger = determine_trigger(
                sig, http_result_param_name, not has_context, args, kwargs
            )
            with trigger.start_as_current_span() as span:
                result = await wrapped(*trigger.args, **trigger.kwargs)
                trigger.set_exit_attributes(span, result)
            return result

        return _async_wrapper(handler)  # pylint:disable=no-value-for-parameter

    @wrapt.decorator(adapter=adapter)
    def _sync_wrapper(wrapped, instance, args, kwargs):
        trigger = determine_trigger(
            sig, http_result_param_name, not has_context, args, kwargs
        )
        with trigger.start_as_current_span() as span:
            result = wrapped(*trigger.args, **trigger.kwargs)
            trigger.set_exit_attributes(span, result)
        return result

    return _sync_wrapper(handler)  # pylint:disable=no-value-for-parameter


def _make_wrapper_adapter(sig: inspect.Signature, is_async: bool) -> HandlerT:
    adapter_src, adapter_locals = _make_wrapper_adapter_src(sig, is_async)

    exec(adapter_src, adapter_locals, adapter_locals)
    adapter = adapter_locals["_adapter"]  # type: HandlerT

    return adapter


def _make_wrapper_adapter_src(
    sig: inspect.Signature, is_async: bool
) -> Tuple[str, Dict[str, Any]]:
    adapter_locals = {}  # type: Dict[str, Any]
    render_pos_only_separator = False
    render_kw_only_separator = True

    context_param = None
    formatted_args = []
    for param in sig.parameters.values():
        formatted = _format_arg(param, adapter_locals)
        kind = param.kind

        if kind == inspect.Parameter.POSITIONAL_ONLY:
            render_pos_only_separator = True
        elif render_pos_only_separator:
            formatted_args.append("/")
            render_pos_only_separator = False

        if kind == inspect.Parameter.VAR_POSITIONAL:
            render_kw_only_separator = False
        elif (
            kind == inspect.Parameter.KEYWORD_ONLY and render_kw_only_separator
        ):
            formatted_args.append("*")
            render_kw_only_separator = False

        if kind == inspect.Parameter.VAR_KEYWORD:
            # insert context before "**kwargs"
            context_param = _make_context_param()
            formatted_args.append(_format_arg(context_param, adapter_locals))

        formatted_args.append(formatted)

    if context_param is None:
        context_param = _make_context_param()
        formatted_args.append(_format_arg(context_param, adapter_locals))

    async_stmt = "async " if is_async else ""
    adapter_sig = ", ".join(formatted_args)
    annot_ret = _get_return_annot_str(sig, adapter_locals)

    # generate adapter function for wrapt
    adapter_src = f"{async_stmt}def _adapter({adapter_sig}){annot_ret}: pass"
    return adapter_src, adapter_locals


def _make_context_param() -> inspect.Parameter:
    return inspect.Parameter(
        KW_CONTEXT,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        default=None,
        annotation=func.Context,
    )


def _format_arg(
    param: inspect.Parameter, adapter_locals: Dict[str, Any]
) -> str:
    if param.kind == inspect.Parameter.VAR_POSITIONAL:
        arg_str = f"*{param.name}"
    elif param.kind == inspect.Parameter.VAR_KEYWORD:
        arg_str = f"**{param.name}"
    else:
        arg_str = param.name
    default_str = _get_default_str(param, adapter_locals)
    annot_str = _get_annot_str(param, adapter_locals)
    return f"{arg_str}{annot_str}{default_str}"


def _get_annot_str(
    param: inspect.Parameter, adapter_locals: Dict[str, Any]
) -> str:
    if param.annotation is inspect.Parameter.empty:
        return ""

    annot_str = f"annot_{param.name}"
    adapter_locals[annot_str] = param.annotation
    return f": {annot_str}"


def _get_return_annot_str(
    sig: inspect.Signature, adapter_locals: Dict[str, Any]
) -> str:
    if sig.return_annotation is inspect.Signature.empty:
        return ""

    annot_str = "annot_return"
    adapter_locals[annot_str] = sig.return_annotation
    return f" -> {annot_str}"


def _get_default_str(
    param: inspect.Parameter, adapter_locals: Dict[str, Any]
) -> str:
    def_value = param.default
    if def_value is inspect.Parameter.empty:
        return ""

    if type(def_value) in _SAFE_REPR_TYPES:
        def_str = repr(def_value)
    else:
        def_str = f"defv_{param.name}"
        adapter_locals[def_str] = def_value

    return f"={def_str}"
