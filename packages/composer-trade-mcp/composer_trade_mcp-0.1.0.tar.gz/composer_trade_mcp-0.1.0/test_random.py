"""
Main MCP server implementation for Composer.
"""
from typing import Dict
import httpx

from src.composer_trade_mcp.server import get_optional_headers
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:2233"

def test_backtest_symphony_by_id(symphony_id: str) -> Dict:
    """
    Backtest a symphony given its ID.
    Use `include_daily_values=False` to reduce the response size (default is True).
    Daily values are cumulative returns since the first day of the backtest (i.e., 19 means 19% cumulative return since the first day).
    If start_date is not provided, the backtest will start from the earliest backtestable date.
    You should default to backtesting from the first day of the year in order to reduce the response size.
    If end_date is not provided, the backtest will end on the last day with data.

    After calling this tool, visualize the results. daily_values can be easily loaded into a pandas dataframe for plotting.
    """
    url = f"{BASE_URL}/api/v1/public/symphonies/{symphony_id}/backtest"
    params = {
        "apply_reg_fee": True,
        "apply_taf_fee": True,
        "broker": "ALPACA_WHITE_LABEL",
        "capital": 100000,
        "slippage_percent": 0.0001,
        "spread_markup": 0.002,
        "benchmark_tickers": ["SPY"],
    }
    params["start_date"] = "2025-06-10"
    token_headers = {"Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg3NzQ4NTAwMmYwNWJlMDI2N2VmNDU5ZjViNTEzNTMzYjVjNThjMTIiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiUm9ubnkgTGkiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUVkRlRwNlVWZEk3T3FodkoxTmFfNnIxTXIzZVJPTkZKdUt5Qm1DX0VhZ3Q9czk2LWMiLCJzdHJpcGVSb2xlIjoicHJvIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2xldmVyaGVhZHMiLCJhdWQiOiJsZXZlcmhlYWRzIiwiYXV0aF90aW1lIjoxNzUwOTQ1Nzk4LCJ1c2VyX2lkIjoiQUZCQUo5MjR0SWUwZDhMOVhBQW1FOEVvVVd0MSIsInN1YiI6IkFGQkFKOTI0dEllMGQ4TDlYQUFtRThFb1VXdDEiLCJpYXQiOjE3NTA5Njg5MDMsImV4cCI6MTc1MDk3MjUwMywiZW1haWwiOiJyb25ueUBpbnZlc3Rjb21wb3Nlci5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJnb29nbGUuY29tIjpbIjExMDc5MTAwNDMzMjEwNTY3NjQ0MSJdLCJlbWFpbCI6WyJyb25ueUBpbnZlc3Rjb21wb3Nlci5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.elrlSPeqymVx6n_r5ZPOcRPWGXU_mruwsirOmk9a1n_aFg3jh5f-ImNDHWW4RxSQPanBDUHfpW3-fwq8lB4J_LYePP-CxqHL-idgtJhShiO2mqrYWMt1ZxPLBOBnwGHYG-pSF4u7nRCX_FRLQIp13C2Znsn73fR5kQQm_bNJb8NtYrqZeKa4YYkmnAoF_cU-mIUNTmaBwG5FGOXUlUL1r7AUSrC9Xh2GdOYWDVZJ8roU0shLtor4pmIVJikqM0T-lI4j8R0Dw_p0YK30tvOD3LEiS7Sw4xZahaioYxLSAbZDeISVkZ0RDwKSppA3lYbf60936UX03-3GPRkZP_x9Rw"}
    api_key_headers = get_optional_headers()
    api_key_headers["x-origin"] = "public-api"
    response = httpx.post(
        url,
        headers=token_headers,
        json=params
    )
    try:
        return response.json()
    except Exception as e:
        return {"error": str(e), "response": response.text}

if __name__ == "__main__":
    print(test_backtest_symphony_by_id("0QMvej3zxKmrupJ4kXDY"))

