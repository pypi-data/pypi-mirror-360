"""Initial Module Data.all SDK.

Source repository: TODO
Documentation: TODO

"""

import logging
import os
import sys
from typing import Any

from dataall_core.dataall_client import BaseClient, DataallClient

from .__metadata__ import __description__, __license__, __title__, __version__

root_logger = logging.getLogger("dataall_sdk")
root_logger.setLevel(os.environ.get("dataall_sdk_loglevel", "INFO").upper())

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

root_logger.addHandler(handler)

__all__ = [
    "__description__",
    "__license__",
    "__title__",
    "__version__",
]


def client(*args: Any, **kwargs: Any) -> BaseClient:
    """Create a low-level service client by name using the default session.

    See :py:meth:`dataall_core.dataall_client.DataallClient.client`.
    """
    da_client_args = {}
    if "schema_version" in kwargs:
        da_client_args["schema_version"] = kwargs.pop("schema_version")
    if "schema_path" in kwargs:
        da_client_args["schema_path"] = kwargs.pop("schema_path")

    return DataallClient(**da_client_args).client(*args, **kwargs)
