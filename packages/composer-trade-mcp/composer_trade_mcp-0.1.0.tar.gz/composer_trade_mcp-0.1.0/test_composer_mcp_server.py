import asyncio
from fastmcp import Client
from fastmcp.client.logging import LogMessage
from composer_trade_mcp.server import mcp

async def log_handler(message: LogMessage):
    level = message.level.upper()
    logger = message.logger or 'server'
    data = message.data
    print(f"[{level}] {logger}: {data}")

client = Client(mcp, log_handler=log_handler)

async def call_tool(tool_name: str, tool_args: dict):
    async with client:
        result = await client.call_tool(tool_name, tool_args, timeout=30.0)
        print(result)

# asyncio.run(call_tool("create_symphony", {
#   "symphony_score": {
#     "id": "a4a94586-2d66-4c7e-b800-5abcb72772e7",
#     "step": "root",
#     "name": "Defensive Crypto Strategy",
#     "description": "A cryptocurrency strategy designed to target maximum drawdown of 30% or less through inverse volatility weighting and defensive asset allocation",
#     "rebalance": "daily",
#     "children": [
#       {
#         "id": "9d658b5d-e451-446c-8fcb-14ae8656b288",
#         "step": "wt-cash-specified",
#         "children": [
#           {
#             "id": "53c353fc-683f-4bab-be8f-85d591b10890",
#             "weight": {
#               "num": 70,
#               "den": 100
#             },
#             "step": "if",
#             "children": [
#               {
#                 "id": "ddd92c26-ed8b-4bb3-b016-784a90767e0a",
#                 "step": "if-child",
#                 "is-else-condition?": False,
#                 "children": [
#                   {
#                     "id": "99f1ac93-7c7a-4efb-a39a-1a370bee1ffe",
#                     "step": "wt-inverse-vol",
#                     "window-days": 30,
#                     "children": [
#                       {
#                         "id": "d53516b0-6448-4443-afbb-83784a546852",
#                         "name": "Bitcoin",
#                         "ticker": "CRYPTO::BTC//USD",
#                         "step": "asset"
#                       },
#                       {
#                         "id": "22093479-614c-4424-a1d9-4ca27ef4a01a",
#                         "name": "Ethereum",
#                         "ticker": "CRYPTO::ETH//USD",
#                         "step": "asset"
#                       },
#                       {
#                         "id": "3cfd5fc3-6490-4736-a0d2-db4fc33c7a0c",
#                         "name": "Solana",
#                         "ticker": "CRYPTO::SOL//USD",
#                         "step": "asset"
#                       }
#                     ]
#                   }
#                 ],
#                 "comparator": "gt",
#                 "lhs-fn": "moving-average-price",
#                 "lhs-val": "CRYPTO::BTC//USD",
#                 # Missing rhs-val, which causes tools that depend on SymphonyScore to crash.
#                 # The error output is so large that it can't be displayed in the Claude Desktop UI.
#                 "rhs-fixed-value?": False,
#                 "rhs-fn": "moving-average-price",
#                 "lhs-window-days": 50,
#                 "rhs-window-days": 200,
#                 "lhs-fn-params": {
#                   "window": 50
#                 },
#                 "rhs-fn-params": {
#                   "window": 200
#                 }
#               },
#               {
#                 "id": "378f23ac-992d-4c68-9580-5df0039157b6",
#                 "step": "if-child",
#                 "is-else-condition?": True,
#                 "children": [
#                   {
#                     "id": "77acb1b4-d028-4e3d-bd98-55483ec25df3",
#                     "name": "Treasury Bills (Cash)",
#                     "ticker": "BIL",
#                     "step": "asset"
#                   }
#                 ]
#               }
#             ]
#           },
#           {
#             "id": "87be8135-c3d3-4f54-bea0-9c819b859b3c",
#             "weight": {
#               "num": 30,
#               "den": 100
#             },
#             "name": "Treasury Bills (Defensive)",
#             "ticker": "BIL",
#             "step": "asset"
#           }
#         ]
#       }
#     ]
#   }
# }))
# Test list_accounts tool
asyncio.run(call_tool("list_accounts", {}))

# asyncio.run(call_tool("backtest_symphony", args))
# Test backtesting public symphony
# asyncio.run(call_tool("backtest_symphony_by_id", {"symphony_id": "czfd4djei67NNWccuLx1", "start_date": "2025-06-10", "include_daily_values": True, "capital": 100000}))
# Test backtesting private symphony
# asyncio.run(call_tool("backtest_symphony_by_id", {"symphony_id": "pk388XU46fGWo3u3gklv", "start_date": "2025-06-10", "include_daily_values": True, "capital": 100000}))
# asyncio.run(call_tool("get_aggregate_portfolio_stats", {"account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7"}))
# asyncio.run(call_tool("get_aggregate_symphony_stats", {"account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7"}))
# asyncio.run(call_tool("get_symphony_daily_performance", {"account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7", "symphony_id": "aTIxEnhrXgj6CuDGyiWS"}))
# asyncio.run(call_tool("get_portfolio_daily_performance", {"account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7"}))
# asyncio.run(call_tool("save_symphony", {
#   "color": "#49D1E3",
#   "hashtag": "#60-40",
#   "symphony_score": {
#     "id": "2766d528-34a1-477c-ad14-21d86a13fb09",
#     "name": "Classic 60-40 Portfolio",
#     "step": "root",
#     "weight": None,
#     "children": [
#       {
#         "id": "48199ca4-1c10-4734-9af5-8a0daf26ab8f",
#         "step": "wt-cash-specified",
#         "weight": None,
#         "children": [
#           {
#             "id": "61c47859-8896-4b16-b654-b70af41c66c1",
#             "name": "Vanguard Total Stock Market ETF",
#             "step": "asset",
#             "ticker": "VTI",
#             "weight": {
#               "den": 100,
#               "num": 60
#             },
#             "exchange": None
#           },
#           {
#             "id": "3c809723-f13e-4e0e-8ab4-a5c76b4beb38",
#             "name": "iShares Core US Aggregate Bond ETF",
#             "step": "asset",
#             "ticker": "AGG",
#             "weight": {
#               "den": 100,
#               "num": 40
#             },
#             "exchange": None
#           }
#         ]
#       }
#     ],
#     "rebalance": "monthly",
#     "description": "A balanced portfolio with 60% allocation to stocks and 40% to bonds, rebalanced monthly for optimal risk-adjusted returns",
#     "rebalance-corridor-width": None
#   }
# }))
# asyncio.run(call_tool("get_saved_symphony", {"symphony_id": "czfd4djei67NNWccuLx1"}))
# asyncio.run(call_tool("get_market_hours", {}))
# asyncio.run(call_tool("invest_in_symphony", {
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "symphony_id": "aTIxEnhrXgj6CuDGyiWS",
#     "amount": 1000.0
# }))
# asyncio.run(call_tool("cancel_invest_or_withdraw", {
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "deploy_id": "036fc602-e09e-494d-98c5-80df0a37498f"}))
# FIXME: This tool is not working.
# asyncio.run(call_tool("withdraw_from_symphony", {
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "symphony_id": "aTIxEnhrXgj6CuDGyiWS",
#     "amount": -100.0
# }))
# asyncio.run(call_tool("skip_automated_rebalance_for_symphony", {
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "symphony_id": "aTIxEnhrXgj6CuDGyiWS",
#     "skip": False
# }))
# asyncio.run(call_tool("go_to_cash_for_symphony", {
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "symphony_id": "aTIxEnhrXgj6CuDGyiWS",
# }))
# asyncio.run(call_tool("preview_rebalance_for_user", {}))
# asyncio.run(call_tool("preview_rebalance_for_symphony", {
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "symphony_id": "aTIxEnhrXgj6CuDGyiWS",
# }))
# asyncio.run(call_tool("rebalance_symphony_now", {
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "symphony_id": "aTIxEnhrXgj6CuDGyiWS",
#     "rebalance_request_uuid": "5d0d72df-746e-4b31-9a3d-855dbcb7bca7"
# }))
# asyncio.run(call_tool("execute_single_trade", {
#     "side": "BUY",
#     "type": "MARKET",
#     "symbol": "HOOD",
#     "notional": 100,
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "time_in_force": "DAY"
# }))
# Expected to throw an error because time_in_force cannot be DAY for a crypto trade.
# asyncio.run(call_tool("execute_single_trade", {
#     "side": "BUY",
#     "type": "MARKET",
#     "symbol": "CRYPTO::SHIB//USD",
#     "notional": "100",
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "time_in_force": "DAY"
# })) 
# Expected to throw an error because notional cannot be negative for a BUY order.
# asyncio.run(call_tool("execute_single_trade", {
#     "side": "BUY",
#     "type": "MARKET",
#     "symbol": "CRYPTO::SHIB//USD",
#     "notional": "-100",
#     "account_uuid": "7d9d336a-465c-482a-b4a0-f3910139d1e7",
#     "time_in_force": "DAY"
# })) 