from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Literal

import typing_extensions

from libpass._utils.bytes import as_str
from libpass.errors import UnknownHashError

if TYPE_CHECKING:
    from collections.abc import Sequence

from libpass.hashers.abc import DisabledHasher, PasswordHasher


class CryptContext:
    def __init__(
        self,
        schemes: Sequence[PasswordHasher],
        deprecated: Literal["auto"] = "auto",
    ) -> None:
        self._schemes = schemes
        self._deprecated = deprecated

        self._validate_init()

    def hash(self, secret: str) -> str:
        scheme = self._default_scheme
        return scheme.hash(secret=secret)

    def verify(self, secret: str, hash: str) -> bool:
        return any(scheme.verify(secret=secret, hash=hash) for scheme in self._schemes)

    def needs_update(self, hash: str) -> bool:
        return all(not scheme.identify(hash) for scheme in self._active_schemes)

    def disable(self, hash: str) -> str:
        hasher = self._default_disabled_hasher
        return as_str(hasher.disable(hash))

    def enable(self, hash: str) -> str:
        for hasher in self._disabled_hashers:
            if hasher.identify(hash):
                return as_str(hasher.enable(hash))

        raise UnknownHashError

    def _validate_init(self) -> None:
        if not self._schemes:
            msg = "At least one scheme must be supplied"
            raise ValueError(msg)

    @functools.cached_property
    def _default_scheme(self) -> PasswordHasher:
        return self._schemes[0]

    @functools.cached_property
    def _active_schemes(self) -> Sequence[PasswordHasher]:
        return tuple(
            scheme for scheme in self._schemes if scheme not in self._deprecated_schemes
        )

    @functools.cached_property
    def _deprecated_schemes(self) -> Sequence[PasswordHasher]:
        if self._deprecated == "auto":
            return self._schemes[1:]

        typing_extensions.assert_never(self._deprecated)

    @functools.cached_property
    def _disabled_hashers(self) -> Sequence[DisabledHasher]:
        return tuple(
            hasher for hasher in self._schemes if isinstance(hasher, DisabledHasher)
        )

    @functools.cached_property
    def _default_disabled_hasher(self) -> DisabledHasher:
        if not self._disabled_hashers:
            msg = "At least one DisabledHasher must be configured"
            raise ValueError(msg)

        return self._disabled_hashers[0]
