"""Stream type classes for tap-belvo."""

from __future__ import annotations

from tap_belvo.client import BelvoStream


class Incomes(BelvoStream):
    """Incomes stream."""

    name = "enrichment_incomes"
    path = "/api/incomes"
    primary_keys = ("id",)
    openapi_ref = "Income"


class RecurringExpenses(BelvoStream):
    """RecurringExpenses stream."""

    name = "enrichment_recurring_expenses"
    path = "/api/recurring-expenses"
    primary_keys = ("id",)
    replication_key = None
    openapi_ref = "RecurringExpenses"


class RiskInsights(BelvoStream):
    """RiskInsights stream."""

    name = "enrichment_risk_insights"
    path = "/api/risk-insights"
    primary_keys = ("id",)
    replication_key = None
    openapi_ref = "RiskInsights"
