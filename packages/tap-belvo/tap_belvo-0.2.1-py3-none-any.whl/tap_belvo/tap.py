"""Belvo tap class."""

from __future__ import annotations

import singer_sdk
from singer_sdk import typing as th

from tap_belvo.streams import banking, core, enrichment, fiscal


class TapBelvo(singer_sdk.Tap):
    """Singer tap for Belvo."""

    name = "tap-belvo"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "secret_id",
            th.StringType,
            description="Belvo API secret ID.",
            required=True,
            secret=True,
        ),
        th.Property(
            "password",
            th.StringType,
            description="Belvo API password.",
            required=True,
            secret=True,
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest datetime to get data from",
        ),
        th.Property(
            "base_url",
            th.StringType,
            description="Base URL for the Belvo API",
            default="https://development.belvo.com",
        ),
    ).to_dict()

    def discover_streams(self) -> list[singer_sdk.Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of Belvo streams.
        """
        # TODO(edgarrmondragon): Add tax declarations and tax returns
        # https://github.com/edgarrmondragon/tap-belvo/issues/76
        return [
            core.Links(self),
            core.Institutions(self),
            # TODO(edgarrmondragon): Register this stream when it's available in the OpenAPI spec  # noqa: E501
            # https://statics.belvo.io/openapi-specs/BelvoOpenFinanceApiSpec.json
            # core.Consents(self),  # noqa: ERA001
            banking.Accounts(self),
            banking.Transactions(self),
            banking.Owners(self),
            # banking.InvestmentPortfolios(self),  # noqa: ERA001
            # banking.ReceivableTransactions(self),  # noqa: ERA001
            enrichment.Incomes(self),
            enrichment.RecurringExpenses(self),
            enrichment.RiskInsights(self),
            fiscal.Invoices(self),
            fiscal.TaxComplianceStatuses(self),
            fiscal.TaxRetentions(self),
            fiscal.TaxStatuses(self),
        ]
