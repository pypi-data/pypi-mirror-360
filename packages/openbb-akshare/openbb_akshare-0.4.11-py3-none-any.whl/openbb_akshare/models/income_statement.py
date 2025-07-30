"""AKShare Income Statement Model."""

# pylint: disable=unused-argument
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_validator


class AKShareIncomeStatementQueryParams(IncomeStatementQueryParams):
    """AKShare Income Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )


class AKShareIncomeStatementData(IncomeStatementData):
    """AKShare Income Statement Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "reported_currency": "CURRENCY",
        "cost_of_revenue": "TOTAL_OPERATE_COST",
        "total_operating_income": "TOTAL_OPERATE_INCOME",
        "total_pre_tax_income": "TOTAL_PROFIT",
        "income_tax_expense": "INCOME_TAX",
        "consolidated_net_income": "NETPROFIT",
        "basic_earnings_per_share": "BASIC_EPS",
        "diluted_earnings_per_share": "DILUTED_EPS",
    }

    reported_currency: Optional[str] = Field(
        default=None,
        description="The currency in which the balance sheet was reported.",
    )
    cost_of_revenue: Optional[float] = Field(
        default=None,
        description="Cost of revenue.",
    )
    total_operating_income: Optional[float] = Field(
        default=None,
        description="Total operating income.",
    )
    total_pre_tax_income: Optional[float] = Field(
        default=None,
        description="Total pre-tax income.",
    )
    income_tax_expense: Optional[float] = Field(
        default=None,
        description="Income tax expense.",
    )
    consolidated_net_income: Optional[float] = Field(
        default=None,
        description="Consolidated net income.",
    )
    basic_earnings_per_share: Optional[float] = Field(
        default=None,
        description="Basic earnings per share.",
    )
    diluted_earnings_per_share: Optional[float] = Field(
        default=None,
        description="Diluted earnings per share.",
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class AKShareIncomeStatementFetcher(
    Fetcher[
        AKShareIncomeStatementQueryParams,
        List[AKShareIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareIncomeStatementQueryParams:
        """Transform the query params."""
        return AKShareIncomeStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: AKShareIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""
        import akshare as ak
        from openbb_akshare.utils.tools import normalize_symbol

        symbol_b, symbol_f, market = normalize_symbol(query.symbol)
        symbol_em = f"SH{symbol_b}"
        stock_profit_sheet_by_yearly_em_df = ak.stock_profit_sheet_by_yearly_em(symbol=symbol_em)
        income_statement_em = stock_profit_sheet_by_yearly_em_df[["REPORT_DATE", "REPORT_TYPE", "CURRENCY", "TOTAL_OPERATE_COST", "TOTAL_OPERATE_INCOME", "TOTAL_PROFIT", "INCOME_TAX", "NETPROFIT", "BASIC_EPS", "DILUTED_EPS"]]

        return income_statement_em.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareIncomeStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AKShareIncomeStatementData]:
        """Return the transformed data."""
        for result in data:
            result.pop("symbol", None)
            result.pop("cik", None)
        return [AKShareIncomeStatementData.model_validate(d) for d in data]
