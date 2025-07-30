"""Stream classes for tap-belvo."""

from __future__ import annotations

from tap_belvo.streams.banking import (
    Accounts,
    Balances,
    InvestmentPortfolios,
    InvestmentTransactions,
    Owners,
    ReceivableTransactions,
    Transactions,
)
from tap_belvo.streams.core import Institutions, Links
from tap_belvo.streams.enrichment import Incomes, RecurringExpenses, RiskInsights
from tap_belvo.streams.fiscal import (
    Invoices,
    TaxComplianceStatuses,
    TaxDeclarations,
    TaxRetentions,
    TaxReturns,
    TaxStatuses,
)

__all__ = [
    "Accounts",
    "Balances",
    "Incomes",
    "Institutions",
    "InvestmentPortfolios",
    "InvestmentTransactions",
    "Invoices",
    "Links",
    "Owners",
    "ReceivableTransactions",
    "RecurringExpenses",
    "RiskInsights",
    "TaxComplianceStatuses",
    "TaxDeclarations",
    "TaxRetentions",
    "TaxReturns",
    "TaxStatuses",
    "Transactions",
]
