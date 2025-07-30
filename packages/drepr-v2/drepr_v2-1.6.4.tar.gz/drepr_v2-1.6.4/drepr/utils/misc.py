from __future__ import annotations

import functools
from typing import Any, Callable, Optional, Sequence, TypeVar, Union

import orjson

V = TypeVar("V")
F = TypeVar("F", bound=Callable)


def assert_not_null(x: Optional[V]) -> V:
    assert x is not None
    return x


def assert_true(x: bool, msg: str) -> bool:
    assert x, msg
    return True


def assert_isinstance(x: Any, cls: type[V]) -> V:
    assert isinstance(x, cls)
    return x


class CacheMethod:
    @staticmethod
    def single_literal_arg(args, _kwargs):
        return args[0]

    @staticmethod
    def as_is_posargs(args, _kwargs):
        return args

    @staticmethod
    def as_is(args, kwargs):
        return (args, tuple(kwargs.items()))

    @staticmethod
    def as_json(args, kwargs):
        return orjson.dumps((args, kwargs))

    @staticmethod
    def selected_args(selection: Sequence[Union[int, str]]):
        selected_args = sorted([x for x in selection if isinstance(x, int)])
        selected_kwargs = sorted([x for x in selection if isinstance(x, str)])

        def fn(args, kwargs):
            sargs = []
            skwargs = {}
            for i in selected_args:
                if i < len(args):
                    sargs.append(args[i])
            for k in selected_kwargs:
                if k in kwargs:
                    skwargs[k] = kwargs[k]
            return orjson.dumps((sargs, skwargs))

        return fn

    @staticmethod
    def cache(
        key: Callable[[tuple, dict], Union[tuple, str, bytes, int]],
        cache_attr: str = "_cache",
    ) -> Callable[[F], F]:
        """Cache instance's method during its life-time.
        Note: Order of the arguments is important. Different order of the arguments will result in different cache key.
        """

        def wrapper_fn(func):
            fn_name = func.__name__

            @functools.wraps(func)
            def fn(self, *args, **kwargs):
                if not hasattr(self, cache_attr):
                    setattr(self, cache_attr, {})
                cache = getattr(self, cache_attr)
                k = (fn_name, key(args, kwargs))
                if k not in cache:
                    cache[k] = func(self, *args, **kwargs)
                return cache[k]

            return fn

        return wrapper_fn  # type: ignore


def get_abs_iri(prefixes: dict[str, str], rel_iri: str) -> str:
    prefix, val = rel_iri.split(":", 1)
    if prefix not in prefixes:
        raise ValueError(
            f"Cannot create absolute IRI because the prefix {prefix} does not exist"
        )
    return f"{prefixes[prefix]}{val}"
