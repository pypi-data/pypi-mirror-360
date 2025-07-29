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

import inspect
from itertools import chain
from typing import Any, Dict, Optional, Sequence, Tuple, Type

from azure import functions as func

KW_CONTEXT = "context"
_POS_PARAMETER_KINDS = (
    inspect.Parameter.POSITIONAL_ONLY,
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
    inspect.Parameter.VAR_POSITIONAL,
)
_NO_VALUE = object()


class InvocationArgs:
    def __init__(
        self,
        sig: inspect.Signature,
        result_param_name: Optional[str],
        drop_context: bool,
        args: Sequence[Any],
        kwargs: Dict[str, Any],
    ):
        self._pos_arg_lookup = _make_pos_arg_lookup(sig)
        self._result_param_name = result_param_name
        self.args = args
        self.kwargs = kwargs.copy()
        self.context = self._get_context()
        if drop_context:
            self.kwargs.pop(KW_CONTEXT, None)

    def _lookup_arg(self, name: str) -> Any:
        arg = self.kwargs.get(name, _NO_VALUE)
        if arg is not _NO_VALUE:
            return arg

        arg_pos = self._pos_arg_lookup.get(name)
        if arg_pos is None:
            return None

        try:
            return self.args[arg_pos]
        except (IndexError, TypeError):
            return None

    def _get_context(self) -> Optional[func.Context]:
        context = self._lookup_arg(KW_CONTEXT)
        return context if _is_context(context) else None

    def get_trigger_param(self, trigger_type: Type[Any]) -> Any:
        trigger_param = None
        for param in chain(self.kwargs.values(), self.args):
            if isinstance(param, trigger_type):
                if trigger_param is not None:
                    return None
                trigger_param = param
        return trigger_param

    def get_out_binding_values(
        self, out_types: Tuple[Type[Any], ...]
    ) -> Sequence[Any]:
        if self._result_param_name:
            binding_name = self._lookup_arg(self._result_param_name)
            if not binding_name:
                return ()

            out_value = _get_out_param_value(binding_name, out_types)
            return () if out_value is _NO_VALUE else (out_value,)

        result = []
        for param in chain(self.kwargs.values(), self.args):
            out_value = _get_out_param_value(param, out_types)
            if out_value is not _NO_VALUE:
                result.append(out_value)
        return result


def _is_context(context: Any) -> bool:
    if context is None:
        return False
    for attr in ("invocation_id", "function_name"):
        if not isinstance(getattr(context, attr, None), str):
            return False
    return True


def _get_out_param_value(
    out_param: Any, out_types: Tuple[Type[Any], ...]
) -> Any:
    if not hasattr(out_param, "get") or not hasattr(out_param, "set"):
        # an Out binding must have a 'get' and a 'set' function
        return _NO_VALUE
    try:
        value = out_param.get()
        return value if isinstance(value, out_types) else _NO_VALUE
    except Exception:  # pylint: disable=broad-except
        return _NO_VALUE


def _make_pos_arg_lookup(sig: inspect.Signature) -> Dict[str, int]:
    arg_lookup = {}
    index = 0
    for param in sig.parameters.values():
        if param.kind in _POS_PARAMETER_KINDS:
            arg_lookup[param.name] = index
            index += 1
        else:
            break
    return arg_lookup
