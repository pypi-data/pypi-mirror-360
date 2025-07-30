"""Fiscal stream type classes for tap-belvo."""

from __future__ import annotations

from tap_belvo.client import BelvoStream


class Invoices(BelvoStream):
    """Invoices stream."""

    name = "fiscal_invoices"
    path = "/api/invoices"
    primary_keys = ("id",)
    replication_key = "created_at"
    openapi_ref = "InvoiceWithIdSat"


class TaxComplianceStatuses(BelvoStream):
    """Tax Compliance Statuses stream."""

    name = "fiscal_tax_compliance_statuses"
    path = "/api/tax-compliance-status"
    primary_keys = ("id",)
    replication_key = "created_at"
    openapi_ref = "TaxComplianceStatus"


# NOTE: This is stream is in beta and its schema is not yet documented.
class TaxDeclarations(BelvoStream):
    """Tax Declarations stream."""

    name = "fiscal_tax_declarations"
    path = "/api/tax-declarations"
    primary_keys = ("id",)
    replication_key = "created_at"
    openapi_ref = "TaxDeclaration"


class TaxRetentions(BelvoStream):
    """Tax Retentions stream."""

    name = "fiscal_tax_retentions"
    path = "/api/tax-retentions"
    primary_keys = ("id",)
    replication_key = "created_at"
    openapi_ref = "TaxRetentions"


class TaxReturns(BelvoStream):
    """Tax Returns stream."""

    name = "fiscal_tax_returns"
    path = "/api/tax-returns"
    primary_keys = ("id",)
    replication_key = "created_at"
    openapi_ref = "TaxReturn"


class TaxStatuses(BelvoStream):
    """Tax Statuses stream."""

    name = "fiscal_tax_statuses"
    path = "/api/tax-status"
    primary_keys = ("id",)
    replication_key = "created_at"
    openapi_ref = "TaxStatusSat"
