"""AKShare Equity Quote Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from pydantic import Field
import logging
from openbb_akshare.utils.tools import setup_logger, normalize_symbol, get_symbol_base

logger = logging.getLogger(__name__)

class AKShareEquityQuoteQueryParams(EquityQuoteQueryParams):
    """AKShare Equity Quote Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class AKShareEquityQuoteData(EquityQuoteData):
    """AKShare Equity Quote Data."""

    __alias_dict__ = {
        "symbol": "代码",
        "name": "名称",
        "last_price": "最新价",
        "open": "今开",
        "high": "最高",
        "low": "最低",
        "prev_close": "昨收",
        "volume": "成交量",
        "change": "涨跌额",
        "change_percent": "涨跌幅",
    }


class AKShareEquityQuoteFetcher(
    Fetcher[AKShareEquityQuoteQueryParams, List[AKShareEquityQuoteData]]
):
    """AKShare Equity Quote Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareEquityQuoteQueryParams:
        """Transform the query."""
        return AKShareEquityQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: AKShareEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from AKShare."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.provider.utils.helpers import get_requests_session
        import akshare as ak

        symbols = query.symbol.split(",")
        all_data = []

        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        stock_quotes = stock_zh_a_spot_em_df[["代码", "名称", "最新价", "今开", "最高", "最低", "涨跌幅", "涨跌额", "成交量", "昨收"]]
        def get_one(symbol):
            """Get the data for one ticker symbol."""
            quote = stock_quotes[stock_quotes["代码"] == symbol]
            if quote.empty:
                return {"symbol": symbol, "error": "Symbol not found"}
            return quote

        for symbol in symbols:
            try:
                # Validate symbol format if applicable (e.g., length, allowed characters)
                if not isinstance(symbol, str) or len(symbol) != 6:
                    raise ValueError(f"Invalid symbol format: {symbol}")
                
                data = get_one(symbol)
                all_data.append(data.to_dict(orient="records")[0])
                
            except Exception as e:
                print(f"Error fetching data for symbol {symbol}: {e}")
                continue
        return all_data

    @staticmethod
    def transform_data(
        query: AKShareEquityQuoteQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[AKShareEquityQuoteData]:
        """Transform the data."""
        return [AKShareEquityQuoteData.model_validate(d) for d in data]
