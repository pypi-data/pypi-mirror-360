"""Core type aliases shared by the client layer."""

from __future__ import annotations

import ssl
from typing import TypeAlias, Union

VerifySSLTypes: TypeAlias = Union[ssl.SSLContext, str, bool]  # pylint: disable=C0103
