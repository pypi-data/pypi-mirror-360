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
import threading
from types import MappingProxyType
from typing import Any, Callable, Dict, Iterator, NamedTuple, Optional

import flask
from opentelemetry import trace as api_trace
from opentelemetry.context import attach, detach
from opentelemetry.context.context import Context
from opentelemetry.propagate import extract
from opentelemetry.trace.span import Span
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.util.types import AttributeValue

from dynatrace.odin.semconv import v1 as semconv
from dynatrace.opentelemetry.gcf._resource import (
    detect_resource,
    get_function_name,
)
from dynatrace.opentelemetry.tracing._logging.loggers import gcf_logger
from dynatrace.opentelemetry.tracing._util.context import (
    set_propagated_resource_attributes,
)
from dynatrace.opentelemetry.tracing._util.exceptions import record_exception
from dynatrace.opentelemetry.tracing._util.http import (
    URL_RELEVANT_HEADERS,
    capture_headers,
)

_INSTRUMENTATION_LIBRARY_NAME = "dynatrace.opentelemetry.gcf"
_FLUSH_TIMEOUT_MILLIS = 6000


class _TriggerGlobals(NamedTuple):
    tracer: api_trace.Tracer
    resource_attrs: Dict[str, AttributeValue]


class Trigger(abc.ABC):
    _TRIGGER_GLOBALS = None  # type: Optional[_TriggerGlobals]
    _TRIGGER_GLOBALS_LOCK = threading.Lock()

    @staticmethod
    def _get_or_prepare_globals() -> _TriggerGlobals:
        if Trigger._TRIGGER_GLOBALS is not None:
            return Trigger._TRIGGER_GLOBALS

        with Trigger._TRIGGER_GLOBALS_LOCK:
            if Trigger._TRIGGER_GLOBALS is not None:
                return Trigger._TRIGGER_GLOBALS

            Trigger._TRIGGER_GLOBALS = _TriggerGlobals(
                tracer=api_trace.get_tracer(_INSTRUMENTATION_LIBRARY_NAME),
                resource_attrs=MappingProxyType(detect_resource()),
            )

            return Trigger._TRIGGER_GLOBALS

    @contextlib.contextmanager
    def start_as_current_span(self, flush_on_exit: bool) -> Iterator[Span]:
        _globals = self._get_or_prepare_globals()
        parent_context = self._extract_parent()

        attrs = _globals.resource_attrs.copy()
        parent_context = set_propagated_resource_attributes(
            attrs, parent_context
        )
        # Set context as active as workaround for: https://github.com/open-telemetry/opentelemetry-python/issues/3350
        ot_context_token = attach(parent_context)

        def _exit_callback():
            try:
                activation.__exit__(None, None, None)
            finally:
                detach(ot_context_token)

            if flush_on_exit:
                _flush_spans()

        self._add_start_attributes(attrs)
        activation = _globals.tracer.start_as_current_span(
            get_function_name() or "invoke",
            parent_context,
            api_trace.SpanKind.SERVER,
            attributes=attrs,
            record_exception=False,
            set_status_on_exception=False,
            end_on_exit=True,
        )
        span = activation.__enter__()  # pylint:disable=unnecessary-dunder-call
        try:
            yield span
        except Exception as ex:  # pylint:disable=broad-except
            record_exception(span, ex)
            span.set_status(Status(StatusCode.ERROR))
            raise ex
        finally:
            self._on_exit(span, _exit_callback)

    def _extract_parent(self) -> Context:  # pylint:disable=no-self-use
        return Context()

    def _add_start_attributes(self, attrs: Dict[str, AttributeValue]) -> None:
        pass

    def set_exit_attributes(self, span: Span, result: Any) -> None:
        pass

    def _on_exit(self, span: Span, exit_callback: Callable[[], None]):  # pylint:disable=no-self-use
        exit_callback()


class GenericTrigger(Trigger):
    def _add_start_attributes(self, attrs: Dict[str, AttributeValue]) -> None:
        attrs[semconv.FAAS_TRIGGER] = semconv.FaasTriggerValues.OTHER.value


class HttpTrigger(Trigger):
    def __init__(self, request: flask.Request):
        self._request = request

    def _extract_parent(self) -> Context:
        return extract(self._request.headers, Context())

    def _add_start_attributes(self, attrs: Dict[str, AttributeValue]) -> None:
        attrs[semconv.FAAS_TRIGGER] = semconv.FaasTriggerValues.HTTP.value
        attrs[semconv.HTTP_URL] = self._request.url
        attrs[semconv.HTTP_METHOD] = self._request.method or "GET"

        # TODO: pass config to capture client-ip headers
        capture_headers(
            attrs, self._get_header_value, exclude=URL_RELEVANT_HEADERS
        )

    def _get_header_value(self, key: str) -> Optional[str]:
        return self._request.headers.get(key)

    def set_exit_attributes(self, span: Span, result: Any) -> None:
        if isinstance(result, flask.Response):
            span.set_attribute(semconv.HTTP_STATUS_CODE, result.status_code)
            if result.status_code >= 500:
                span.set_status(Status(StatusCode.ERROR))

    def _on_exit(self, span: Span, exit_callback: Callable[[], None]):
        def _after_request(response: flask.Response) -> flask.Response:
            self.set_exit_attributes(span, response)
            exit_callback()

            return response

        try:
            # defer span end until the current flask request is finished
            flask.after_this_request(_after_request)
        except Exception as ex:  # pylint: disable=broad-except
            gcf_logger.warning(
                "Error when registering 'flask.after_this_request' callback: %s",
                ex,
            )
            exit_callback()


def _flush_spans() -> None:
    tracer_provider = api_trace.get_tracer_provider()
    if hasattr(tracer_provider, "force_flush"):
        tracer_provider.force_flush(_FLUSH_TIMEOUT_MILLIS)


def determine_trigger(args, kwargs) -> Trigger:
    arglist = [*args, *kwargs.values()]
    if len(arglist) == 1 and isinstance(arglist[0], flask.Request):
        return HttpTrigger(arglist[0])

    return GenericTrigger()
