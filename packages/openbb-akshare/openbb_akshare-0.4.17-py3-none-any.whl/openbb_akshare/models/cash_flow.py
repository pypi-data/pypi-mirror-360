"""AKShare Cash Flow Statement Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class AKShareCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """AKShare Cash Flow Statement Query.

    Source: https://finance.yahoo.com/
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
    limit: Optional[int] = Field(
        default=5,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
        le=5,
    )


class AKShareCashFlowStatementData(CashFlowStatementData):
    """AKShare Cash Flow Statement Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "reported_currency": "CURRENCY",
    }

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class AKShareCashFlowStatementFetcher(
    Fetcher[
        AKShareCashFlowStatementQueryParams,
        list[AKShareCashFlowStatementData],
    ]
):
    """AKShare Cash Flow Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> AKShareCashFlowStatementQueryParams:
        """Transform the query parameters."""
        return AKShareCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareCashFlowStatementQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the AKShare endpoints."""
        # pylint: disable=import-outside-toplevel
        import akshare as ak
        import pandas as pd
        from openbb_akshare.utils.tools import normalize_symbol

        symbol_b, symbol_f, market = normalize_symbol(query.symbol)
        symbol_em = f"SH{symbol_b}"
        stock_cash_flow_sheet_by_yearly_em_df = ak.stock_cash_flow_sheet_by_yearly_em(symbol=symbol_em)
        cash_flow_em = stock_cash_flow_sheet_by_yearly_em_df[["REPORT_DATE", "REPORT_TYPE", "CURRENCY",
            "TOTAL_OPERATE_INFLOW", "TOTAL_OPERATE_OUTFLOW", "NETCASH_OPERATE", 
            "TOTAL_INVEST_INFLOW", "TOTAL_INVEST_OUTFLOW", "NETCASH_INVEST", 
            "TOTAL_FINANCE_INFLOW", "TOTAL_FINANCE_OUTFLOW","NETCASH_FINANCE", "NETPROFIT"]]

        return cash_flow_em.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareCashFlowStatementQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AKShareCashFlowStatementData]:
        """Transform the data."""
        return [AKShareCashFlowStatementData.model_validate(d) for d in data]
