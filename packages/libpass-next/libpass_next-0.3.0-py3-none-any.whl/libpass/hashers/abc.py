import typing
from typing import Protocol

from libpass._utils.bytes import StrOrBytes

__all__ = ["DisabledHasher", "PasswordHasher"]


class PasswordHasher(Protocol):
    def hash(self, secret: StrOrBytes) -> str: ...

    def verify(self, hash: StrOrBytes, secret: StrOrBytes) -> bool: ...

    def identify(self, hash: StrOrBytes) -> bool: ...

    def needs_update(self, hash: StrOrBytes) -> bool:
        """Check if hash needs to be updated, returns True if password is not recognized."""
        ...


@typing.runtime_checkable
class DisabledHasher(Protocol):
    def identify(self, hash: StrOrBytes) -> bool: ...

    def enable(self, hash: StrOrBytes) -> StrOrBytes: ...

    def disable(self, hash: StrOrBytes) -> StrOrBytes: ...
