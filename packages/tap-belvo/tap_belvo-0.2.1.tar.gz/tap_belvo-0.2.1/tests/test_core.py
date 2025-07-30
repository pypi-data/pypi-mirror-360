"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from typing import Any
from urllib.parse import ParseResult

from requests import Response
from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_belvo.client import BelvoPaginator
from tap_belvo.tap import TapBelvo

SAMPLE_CONFIG: dict[str, Any] = {}


TestTapBelvo = get_tap_test_class(
    TapBelvo,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        ignore_no_records_for_streams=[
            "banking_accounts",
            "banking_balances",
            "banking_owners",
            "banking_transactions",
            "enrichment_incomes",
            "enrichment_recurring_expenses",
            "enrichment_risk_insights",
            "fiscal_invoices",
            "fiscal_tax_compliance_statuses",
            "fiscal_tax_retentions",
            "fiscal_tax_statuses",
            "links",
        ],
    ),
)


def test_paginator() -> None:
    """Validate paginator that uses the page offset."""
    response = Response()
    paginator = BelvoPaginator()

    assert not paginator.finished
    assert paginator.current_value is None

    response._content = (
        b'{"next": "https://sandbox.belvo.com/api/accounts/?page=2&page_size=100"}'
    )
    paginator.advance(response)
    assert not paginator.finished
    assert paginator.current_value == ParseResult(
        scheme="https",
        netloc="sandbox.belvo.com",
        path="/api/accounts/",
        params="",
        query="page=2&page_size=100",
        fragment="",
    )
    assert paginator.count == 1

    response._content = b'{"next": null}'
    paginator.advance(response)
    assert paginator.finished
    assert paginator.count == 2  # type: ignore[unreachable] # noqa: PLR2004
