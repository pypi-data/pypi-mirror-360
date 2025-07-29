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

import abc
import contextlib
import inspect
import threading
from typing import Any, Dict, Iterator, Optional, Sequence, Union

from azure import functions as func
from opentelemetry.context.context import Context
from opentelemetry.propagate import extract
from opentelemetry.trace import SpanKind, Tracer, get_tracer
from opentelemetry.trace.span import Span
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.util.types import AttributeValue

from dynatrace.odin.semconv import v1 as semconv
from dynatrace.opentelemetry.azure.functions._bindings import InvocationArgs
from dynatrace.opentelemetry.azure.functions._resource import detect_resource
from dynatrace.opentelemetry.tracing._util.context import (
    propagate_resource_attributes,
)
from dynatrace.opentelemetry.tracing._util.exceptions import record_exception
from dynatrace.opentelemetry.tracing._util.http import (
    URL_RELEVANT_HEADERS,
    capture_headers,
)

_INSTRUMENTATION_LIBRARY_NAME = "dynatrace.opentelemetry.azure.functions"
_UNKNOWN_BINDING = object()


class Trigger(abc.ABC):
    _TRACER_LOCK = threading.Lock()
    _TRACER = None

    def __init__(self, trigger_param: Any, invoke_args: InvocationArgs):
        self._trigger_param = trigger_param
        self._invoke_args = invoke_args
        self.args = invoke_args.args
        self.kwargs = invoke_args.kwargs

    @contextlib.contextmanager
    def start_as_current_span(self) -> Iterator[Span]:
        tracer = self._get_tracer()
        attributes = detect_resource(self._invoke_args.context)
        parent_context = self._extract_parent()

        # Set context as active as workaround for: https://github.com/open-telemetry/opentelemetry-python/issues/3350
        with propagate_resource_attributes(
            attributes, parent_context
        ) as parent_context:
            self._add_start_attributes(attributes)

            with tracer.start_as_current_span(
                self._get_function_name(),
                parent_context,
                SpanKind.SERVER,
                attributes=attributes,
                record_exception=False,
                set_status_on_exception=False,
                end_on_exit=True,
            ) as span:
                try:
                    yield span
                except BaseException as ex:
                    self._on_exception(span, ex)
                    raise ex

    def _get_tracer(self) -> Tracer:
        tracer = Trigger._TRACER
        if tracer is not None:
            return tracer

        with self._TRACER_LOCK:
            tracer = Trigger._TRACER
            if tracer is not None:
                return tracer

            tracer = get_tracer(_INSTRUMENTATION_LIBRARY_NAME)
            Trigger._TRACER = tracer
            return tracer

    def _get_function_name(self) -> str:
        if self._invoke_args.context is not None:
            return self._invoke_args.context.function_name
        return "invoke"

    @abc.abstractmethod
    def _extract_parent(self) -> Context:
        pass

    @abc.abstractmethod
    def _add_start_attributes(self, attrs: Dict[str, AttributeValue]) -> None:
        pass

    def _on_exception(  # pylint:disable=no-self-use
        self, span: Span, exception: BaseException
    ) -> None:
        if span.is_recording():
            record_exception(span, exception)
            span.set_status(Status(StatusCode.ERROR))

    def set_exit_attributes(self, span: Span, result: Any) -> None:
        pass


class GenericTrigger(Trigger):
    def _extract_parent(self) -> Context:
        return Context()

    def _add_start_attributes(self, attrs: Dict[str, AttributeValue]) -> None:
        attrs[semconv.FAAS_TRIGGER] = semconv.FaasTriggerValues.OTHER.value


class HttpTrigger(Trigger):
    _RESPONSE_TYPES = (func.HttpResponse, str, type(None))

    def _extract_parent(self):
        req = self._trigger_param  # type: func.HttpRequest
        return extract(req.headers, Context())

    def _get_header_value(self, key: str) -> Optional[str]:
        req = self._trigger_param  # type: func.HttpRequest
        return req.headers.get(key)

    def _add_start_attributes(self, attrs: Dict[str, AttributeValue]) -> None:
        req = self._trigger_param  # type: func.HttpRequest

        attrs[semconv.FAAS_TRIGGER] = semconv.FaasTriggerValues.HTTP.value
        attrs[semconv.HTTP_METHOD] = req.method or "GET"
        attrs[semconv.HTTP_URL] = req.url

        # TODO: pass config to capture client-ip headers
        capture_headers(
            attrs, self._get_header_value, exclude=URL_RELEVANT_HEADERS
        )

    def set_exit_attributes(
        self, span: Span, result: Optional[Union[func.HttpResponse, str]]
    ) -> None:
        if result is None:
            result = self._response_from_out_binding()

        if result is _UNKNOWN_BINDING:
            return

        if isinstance(result, func.HttpResponse):
            status_code = result.status_code
            span.set_attribute(semconv.HTTP_STATUS_CODE, status_code)
            if status_code >= 500:
                span.set_status(Status(StatusCode.ERROR))
        else:
            status_code = 200 if result is not None else 204
            span.set_attribute(semconv.HTTP_STATUS_CODE, status_code)

    def _response_from_out_binding(self) -> Any:
        out_bindings = self._invoke_args.get_out_binding_values(
            self._RESPONSE_TYPES
        )
        if len(out_bindings) != 1:
            return _UNKNOWN_BINDING

        binding_value = out_bindings[0]
        return binding_value


_TRIGGER_MAPPING = {func.HttpRequest: HttpTrigger}


def determine_trigger(
    sig: inspect.Signature,
    out_binding: Optional[str],
    drop_context: bool,
    args: Sequence[Any],
    kwargs: Dict[str, Any],
) -> Trigger:
    invoke_args = InvocationArgs(sig, out_binding, drop_context, args, kwargs)
    for trigger_type, trigger_class in _TRIGGER_MAPPING.items():
        trigger_value = invoke_args.get_trigger_param(trigger_type)
        if trigger_value is not None:
            return trigger_class(trigger_value, invoke_args)
    return GenericTrigger(None, invoke_args)
