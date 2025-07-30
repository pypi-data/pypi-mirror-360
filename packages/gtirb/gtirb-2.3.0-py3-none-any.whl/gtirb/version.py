# Get the version from the package's version, so the version can be defined in
# setup.py alone.
API_VERSION = (
    "2."
    "3."
    "0"
    ""
)  # type: str
"""The semantic version of this API."""

PROTOBUF_VERSION = 4  # type: int
"""The version of Protobuf this API can read and write from.
Attempts to load old Protobuf versions will raise a ``ValueError``.
"""
