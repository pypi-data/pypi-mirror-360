import requests
import pandas as pd
from fastmcp.server.middleware import Middleware, MiddlewareContext
import json
import os
import yaml
from .prompt import sys_prompt, ui_design, data_views, stock_data
import sys
import contextlib
from io import StringIO
from dotenv import load_dotenv
import pyotp
from growwapi import GrowwAPI
import time
import threading


class GrowwSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._groww = None
                    cls._instance._initialized = False
        return cls._instance

    def get_api(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._groww = self._init_login()
                    self._initialized = True
        return self._groww

    def _init_login(self):
        load_dotenv()
        API_AUTH_TOKEN = os.getenv("GROWW_API_AUTH_TOKEN")
        API_AUTH_KEY = os.getenv("GROWW_API_KEY")
        API_AUTH_SECRET = os.getenv("GROWW_API_SECRET")

        try:
            # First priority: Use API Key and Secret with TOTP
            if API_AUTH_KEY and API_AUTH_SECRET:
                try:
                    totp_gen = pyotp.TOTP(API_AUTH_SECRET)
                    totp = totp_gen.now()
                    access_token = GrowwAPI.get_access_token(API_AUTH_KEY, totp)
                    with suppress_stdout():
                        time.sleep(1)
                        return GrowwAPI(access_token)
                except Exception as e:
                    raise ValueError(
                        f"Failed to authenticate with API Key and Secret: {str(e)}"
                    )

            # Second priority: Use Auth Token
            elif API_AUTH_TOKEN:
                try:
                    with suppress_stdout():
                        time.sleep(1)
                        return GrowwAPI(API_AUTH_TOKEN)
                except Exception as e:
                    raise ValueError(
                        f"Failed to authenticate with API Auth Token: {str(e)}"
                    )

            # No credentials available
            else:
                raise ValueError(
                    "Authentication credentials not found. Please provide either API_AUTH_TOKEN or both API_AUTH_KEY and API_AUTH_SECRET in environment variables."
                )

        except Exception as e:
            # Re-raise with context if it's already a ValueError, otherwise wrap it
            if isinstance(e, ValueError):
                raise e
            else:
                raise ValueError(f"Groww login failed: {str(e)}")


@contextlib.contextmanager
def suppress_stdout():
    """Context manager to suppress stdout temporarily"""
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def groww_login():
    """Get the GrowwAPI instance using singleton pattern"""
    return GrowwSingleton().get_api()


def load_system_instructions():
    """Load the comprehensive system instructions from YAML"""
    try:

        instructions = f"""
            IMPORTANT: You are a Groww trading assistant. Follow these behavioral guidelines strictly:

            {sys_prompt}

            ## Additional Guidelines:

            ### UI Design Instructions:
            {ui_design}

            ### Data Analysis Instructions:
            {data_views}

            ### Stock Data Handling:
            {stock_data}

            CRITICAL: Always follow the Pre-Execution Confirmation and Post-Action Verification rules above. Never place orders without explicit user confirmation.
            """
        return instructions.strip()

    except Exception as e:
        # print(f"Warning: Could not load system instructions: {e}")
        return "A comprehensive MCP Server for Groww trading platform. IMPORTANT: Always ask for user confirmation before placing any orders."


class LoggingMiddleware(Middleware):

    async def on_message(self, context: MiddlewareContext, call_next):
        with open("logs.jsonl", "a+") as f:
            try:
                result = await call_next(context)

                f.write(
                    json.dumps(
                        {
                            "method": context.method,
                            "source": context.source,
                            "message": context.message,
                            "timestamp": context.timestamp,
                            "result": result,
                            "error": None,
                        },
                        indent=2,
                        default=str,
                    )
                    + "\n"
                )
                # print(f"Completed {context.method}")

                return result
            except Exception as e:
                f.write(
                    json.dumps(
                        {
                            "method": context.method,
                            "source": context.source,
                            "message": context.message,
                            "timestamp": context.timestamp,
                            "result": None,
                            "error": str(e),
                        },
                        indent=2,
                        default=str,
                    )
                    + "\n"
                )
                # print(f"Error: {context.method} {context.source} {context.message} {e}")
                raise e


def get_symbol_match(company_name) -> list[dict]:

    SEARCH_PARAMS = {"page": "0", "entity_type": "Stocks", "size": "3", "web": "true"}
    SEARCH_HEADERS = {
        "Cookie": "__cf_bm=3zuiAWWCCpivAO_jzOiryxtvz7ZypXVmUb17qbpxo_s-1714125909-1.0.1.1-FPTj_.Kv_fLvfcpwoOdKl4E6zwg.0MRkDyxA9LwdDoVTZl572sEYRDR9WfNlaBp.CteyIZU1CX29gtjPfLY78A; __cfruid=d24ab831abe714138f69218475637cfe9ca9e4b3-1714125909; _cfuvid=RPSaGCchAKgVJKtPIuhV9ZuHiWrkDLTSy952aYgQoMA-1714125909853-0.0.1.1-604800000",
    }
    SEARCH_API_URL = "https://groww.in/v1/api/search/v3/query/global/st_query_no_pop"

    try:

        params = {**SEARCH_PARAMS, "query": company_name}
        response = requests.get(SEARCH_API_URL, headers=SEARCH_HEADERS, params=params)
        response.raise_for_status()
        data = pd.DataFrame(response.json()["data"]["content"])

        return (
            data[
                [
                    "entity_type",
                    "company_short_name",
                    "title",
                    "id",
                    "search_id",
                    "nse_scrip_code",
                    "bse_scrip_code",
                ]
            ]
            .rename(
                columns={
                    "nse_scrip_code": "nse_symbol_ticker",
                    "bse_scrip_code": "bse_symbol_ticker",
                }
            )
            .to_dict(orient="records")
        )

    except Exception as e:
        # print(
        #     f"Error in getting ISIN code for stock using API: {company_name} with exception: {e}"
        # )
        # print(f"Query: {company_name} Response: {response.text}", e)

        return None
