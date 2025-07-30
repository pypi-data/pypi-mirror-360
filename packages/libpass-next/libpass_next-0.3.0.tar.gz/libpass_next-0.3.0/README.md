# libpass-next
Libpass is a rewrite of passlib library


## Installation
```shell
pip install libpass-next
```

## Usage
You can use individual hashers (argon2, bcrypt, pbkdf2, etc) individually:
```python
from libpass.hashers.bcrypt import BcryptHasher

hasher = BcryptHasher()

hash = hasher.hash("password")
print(f"{hash=}")

is_valid = hasher.verify(hash=hash, secret="password")
print(f"{is_valid=}")

```

Or you can combine them into a single `CryptContext` if you
need to support multiple password hashing schemes:
```python
from libpass.context import CryptContext
from libpass.hashers.argon2 import Argon2Hasher
from libpass.hashers.bcrypt import BcryptHasher

context = CryptContext(
    schemes=[
        Argon2Hasher(),
        BcryptHasher(),
    ]
)

hash = context.hash("password")
# $argon2id$v=19$m=65536,t=3,p=4$cIRqyLJEF2IBc0ggxp4Kqw$W+PxOyErga7uHi/BOkyTsT6atZAfFuc1GEPwHOwyJMM
print(f"{hash=}")

is_valid = context.verify(hash=hash, secret="password")
print(f"{is_valid=}")  # True

old_hash = "$2b$12$eNeQerKdKhGj3IfERBdGPem7wUtlW3szwawvT5GIm/UNKxCuDnZku"
print(context.verify(hash=old_hash, secret="password"))  # True
print(context.needs_update(old_hash))  # True
```
