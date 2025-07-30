"""AKShare Balance Sheet Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class AKShareBalanceSheetQueryParams(BalanceSheetQueryParams):
    """AKShare Balance Sheet Query.

    Source: https://akshare.akfamily.xyz/data/stock/stock.html#id180
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


class AKShareBalanceSheetData(BalanceSheetData):
    """AKShare Balance Sheet Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "fiscal_year": "REPORT_DATE_NAME",
        "totalEquity": "TOTAL_EQUITY",
        "totalDebt": "TOTAL_LIABILITIES",
        "totalAssets": "TOTAL_ASSETS"
    }

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return datetime object from string."""
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S").date()
        return v


class AKShareBalanceSheetFetcher(
    Fetcher[
        AKShareBalanceSheetQueryParams,
        list[AKShareBalanceSheetData],
    ]
):
    """AKShare Balance Sheet Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> AKShareBalanceSheetQueryParams:
        """Transform the query parameters."""
        return AKShareBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareBalanceSheetQueryParams,
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
        stock_balance_sheet_by_yearly_em_df = ak.stock_balance_sheet_by_yearly_em(symbol=symbol_em)
        balance_sheet_em = stock_balance_sheet_by_yearly_em_df[["REPORT_DATE", "REPORT_TYPE", "REPORT_DATE_NAME", "TOTAL_ASSETS", "TOTAL_LIABILITIES", "TOTAL_EQUITY"]]
        balance_sheet_em['REPORT_DATE_NAME'] = pd.to_datetime(balance_sheet_em['REPORT_DATE']).dt.year.astype(int)

        return balance_sheet_em.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareBalanceSheetQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[AKShareBalanceSheetData]:
        """Transform the data."""
        return [AKShareBalanceSheetData.model_validate(d) for d in data]
