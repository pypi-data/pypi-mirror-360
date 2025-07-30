from typing import Final

from libpass._utils.bytes import StrOrBytes, as_str
from libpass.hashers.abc import DisabledHasher, PasswordHasher


class UnixDisabled(PasswordHasher, DisabledHasher):
    def __init__(self, prefix: str = "!") -> None:
        self.prefix: Final = prefix

    def hash(self, secret: StrOrBytes) -> str:  # noqa: ARG002
        return self.prefix

    def identify(self, hash: StrOrBytes) -> bool:
        return as_str(hash).startswith(self.prefix)

    def verify(self, hash: StrOrBytes, secret: StrOrBytes) -> bool:  # noqa: ARG002
        return False

    def needs_update(self, hash: StrOrBytes) -> bool:  # noqa: ARG002
        return False

    def enable(self, hash: StrOrBytes) -> str:
        hash_as_str = as_str(hash)
        if not hash_as_str.startswith(self.prefix):
            return hash_as_str
        return hash_as_str.removeprefix(self.prefix)

    def disable(self, hash: StrOrBytes) -> str:
        hash_as_str = as_str(hash)
        if hash_as_str.startswith(self.prefix):
            return hash_as_str
        return self.prefix + hash_as_str
