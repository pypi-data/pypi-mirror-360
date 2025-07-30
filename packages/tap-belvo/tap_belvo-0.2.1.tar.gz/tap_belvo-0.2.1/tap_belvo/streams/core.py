"""Stream type classes for tap-belvo."""

from __future__ import annotations

import typing as t

from tap_belvo.client import BelvoStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class Links(BelvoStream):
    """Links stream."""

    name = "links"
    path = "/api/links"
    primary_keys = ("id",)
    replication_key = "created_at"
    openapi_ref = "Link"

    def get_child_context(
        self,
        record: dict[str, t.Any],
        context: Context | None,  # noqa: ARG002
    ) -> dict[t.Any, t.Any]:
        """Return the child context.

        Args:
            record: The record to get the child context for.
            context: The parent context.

        Returns:
            The child context.
        """
        return {"link_id": record["id"]}


class Institutions(BelvoStream):
    """Institutions stream."""

    name = "institutions"
    path = "/api/institutions"
    primary_keys = ("id",)
    replication_key = None
    openapi_ref = "Institution"


class Consents(BelvoStream):
    """Consents stream."""

    name = "consents"
    path = "/api/consents"
    primary_keys = ("id",)
    replication_key = None
    openapi_ref = "Consent"
