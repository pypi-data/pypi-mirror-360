"""OpenAPI 3.0.0 specification for the Belvo API."""

from __future__ import annotations

import json
import logging
from functools import cache
from importlib import resources
from typing import Any

logger = logging.getLogger(__name__)


@cache
def load_openapi() -> dict[str, Any]:
    """Load the OpenAPI specification from the package.

    Returns:
        The OpenAPI specification as a dict.
    """
    logger.info("Loading OpenAPI spec from package")
    filename = "BelvoOpenFinanceApiSpec.json"
    with resources.files(__package__).joinpath(filename).open() as f:
        return json.load(f)  # type: ignore[no-any-return]
