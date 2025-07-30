from __future__ import annotations

from collections import Counter, defaultdict
from functools import cached_property
from typing import Mapping, Optional, Union

from drepr.utils.misc import get_abs_iri


class NamespaceMixin:
    prefixes: dict[str, str]

    @cached_property
    def namespace_manager(self):
        return NamespaceManager.from_prefix2ns(self.prefixes)

    @classmethod
    def is_rel_iri(cls, iri: str) -> bool:
        return iri.find("://") == -1 and iri.find(":") != -1

    def get_rel_iri(self, abs_iri: str) -> str:
        """Convert an absolute IRI to a relative IRI."""
        assert not self.is_rel_iri(abs_iri)
        prefix = self.namespace_manager.prefix_index.get(abs_iri)
        if prefix is None:
            raise ValueError(
                "Cannot create relative IRI because there is no suitable prefix"
            )
        ns = self.prefixes[prefix]
        return f"{prefix}:{abs_iri[len(ns):]}"

    def get_abs_iri(self, rel_iri: str) -> str:
        """Convert a relative IRI to an absolute IRI."""
        assert self.is_rel_iri(rel_iri), rel_iri
        return get_abs_iri(self.prefixes, rel_iri)


class NamespaceManager:
    """A helper class for converting between absolute URI and relative URI."""

    __slots__ = ("prefix2ns", "ns2prefix", "prefix_index", "prefix2len")

    def __init__(
        self,
        prefix2ns: dict[str, str],
        ns2prefix: dict[str, str],
        prefix_index: PrefixIndex,
    ):
        self.prefix2ns = prefix2ns
        self.ns2prefix = ns2prefix
        self.prefix_index = prefix_index
        self.prefix2len = {prefix: len(ns) for prefix, ns in prefix2ns.items()}

    @classmethod
    def from_prefix2ns(cls, prefix2ns: dict[str, str]):
        ns2prefix = {v: k for k, v in prefix2ns.items()}
        if len(ns2prefix) != len(prefix2ns):
            raise Exception(
                "Duplicated namespaces: %s"
                % [k for k, v in Counter(prefix2ns.values()).items() if v > 1]
            )
        prefix_index = PrefixIndex.create(ns2prefix)

        return cls(prefix2ns, ns2prefix, prefix_index)

    def normalizeUri(self, uri: str) -> str:
        prefix = self.prefix_index.get(uri)
        if prefix is None:
            return f"<{uri}>"
        return f"{prefix}:{uri[self.prefix2len[prefix]:]}"


class PrefixIndex:
    """Namespace indexing so we can quickly get prefix of a URI."""

    __slots__ = ("index", "start", "end")

    def __init__(
        self, index: dict[str, PrefixIndex | str], start: int, end: int
    ) -> None:
        self.index = index
        self.start = start
        self.end = end

    @staticmethod
    def create(ns2prefix: Mapping[str, str]):
        sorted_ns = sorted(ns2prefix.keys(), key=lambda x: len(x), reverse=True)
        if len(sorted_ns) == 0:
            raise Exception("No namespace provided")

        return PrefixIndex._create(ns2prefix, sorted_ns, 0)

    @staticmethod
    def _create(ns2prefix: Mapping[str, str], nses: list[str], start: int):
        shortest_ns = nses[-1]
        index = PrefixIndex({}, start, len(shortest_ns))

        if index.start == index.end:
            # we have an empty key, it must have more than one element because of the previous call
            index.index[""] = ns2prefix[nses[-1]]
            subindex = PrefixIndex._create(ns2prefix, nses[:-1], index.end)
            for key, node in subindex.index.items():
                index.index[key] = node
            return index

        tmp = defaultdict(list)
        for ns in nses:
            key = ns[index.start : index.end]
            tmp[key].append(ns)

        for key, lst_ns in tmp.items():
            if len(lst_ns) == 1:
                index.index[key] = ns2prefix[lst_ns[0]]
            else:
                index.index[key] = PrefixIndex._create(ns2prefix, lst_ns, index.end)
        return index

    def get(self, uri: str) -> Optional[str]:
        """Get prefix of an uri. Return None if it is not found"""
        key = uri[self.start : self.end]
        if key in self.index:
            value = self.index[key]
            if isinstance(value, PrefixIndex):
                return value.get(uri)
            return value

        if "" in self.index:
            return self.index[""]  # type: ignore

        return None

    def __str__(self):
        """Readable version of the index"""
        stack: list[tuple[int, str, Union[str, PrefixIndex]]] = list(
            reversed([(0, k, v) for k, v in self.index.items()])
        )
        out = []

        while len(stack) > 0:
            depth, key, value = stack.pop()
            indent = "    " * depth
            if isinstance(value, str):
                out.append(indent + "`" + key + "`: " + value + "\n")
            else:
                out.append(indent + "`" + key + "`:" + "\n")
                for k, v in value.index.items():
                    stack.append((depth + 1, k, v))

        return "".join(out)

    def to_dict(self):
        return {
            k: v.to_dict() if isinstance(v, PrefixIndex) else v
            for k, v in self.index.items()
        }
