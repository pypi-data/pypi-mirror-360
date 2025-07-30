# import logging
# import urllib.parse
# import requests
# import json
# from typing import List
# from utils import validate_date, validate_symbols, validate_quote

# logger = logging.getLogger(__name__)


# class CommodityAPI:
#     # API client for accessing commodity rates and related data from the API Freaks service.
#     def __init__(self, api_key: str):
#         self.api_key = api_key

#     # Helper method to make a GET request to the API and handle errors.
#     # This method abstracts the request logic to avoid code duplication across different API methods.
#     def _make_request(self, url: str) -> dict:
#         """
#         Helper method to make a GET request and handle HTTP errors gracefully.
#         """
#         headers = {
#             "X-apiKey": self.api_key
#         }
#         try:
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()  # Raise HTTPError if response code is 4xx or 5xx
#             data = response.json()
#             data = json.dumps(data, indent=4)  # ✅ Pretty output
#             return data
#         except requests.exceptions.HTTPError as http_err:
#             error_message = {
#                 "error": f"HTTP Error: {http_err}",
#                 "status_code": response.status_code,
#                 "url": url
#             }
#             error_message= json.dumps(error_message, indent=4) # ✅ Pretty print error
#             return error_message
#         except requests.exceptions.RequestException as req_err:
#             error_message = {
#                 "error": f"Request Error: {req_err}",
#                 "url": url
#             }
#             error_message= json.dumps(error_message, indent=4) # ✅ Pretty print error
#             return error_message
#         except ValueError as val_err:
#             error_message = {
#                 "error": f"JSON Decode Error: {val_err}",
#                 "url": url
#             }
#             error_message= json.dumps(error_message, indent=4) # ✅ Pretty print error
#             return error_message

#     # Methods to interact with the API for various commodity-related data.
#     def get_live_rates(self, symbols: List[str], updates: str = "1m", quote: str = "USD") -> dict:
#         if not validate_symbols(symbols):
#             raise ValueError("Invalid input symbols.")
#         if updates not in ["1m", "10m"]:
#             raise ValueError("Invalid update interval.")
#         if not validate_quote(quote):
#             raise ValueError("Invalid quote currency.")

#         params = {
#             "symbols": ", ".join(symbols),
#             "updates": updates,
#             "quote": quote
#         }
#         url = f"https://api.apifreaks.com/v1.0/commodity/rates/latest?{urllib.parse.urlencode(params)}"
#         return self._make_request(url)

#     # Method to get historical commodity rates for a specific date.
#     # It validates the input symbols and date before making the request.
#     def get_historical_rates(self, symbols: List[str], date: str) -> dict:
#         if not validate_symbols(symbols):
#             raise ValueError("Invalid symbols.")
#         if not validate_date(date):
#             raise ValueError("Invalid date.")

#         params = {
#             "symbols": ", ".join(symbols),
#             "date": date
#         }
#         url = f"https://api.apifreaks.com/v1.0/commodity/rates/historical?{urllib.parse.urlencode(params)}"
#         return self._make_request(url)

#     # Methods to get commodity fluctuation and time series data.
#     # These methods validate the input symbols and date range before making the request.
#     def get_fluctuation(self, symbols: List[str], start_date: str, end_date: str) -> dict:
#         if not validate_symbols(symbols):
#             raise ValueError("Invalid symbols.")
#         if not validate_date(start_date) or not validate_date(end_date):
#             raise ValueError("Invalid date range.")

#         params = {
#             "symbols": ", ".join(symbols),
#             "startDate": start_date,
#             "endDate": end_date
#         }
#         url = f"https://api.apifreaks.com/v1.0/commodity/fluctuation?{urllib.parse.urlencode(params)}"
#         return self._make_request(url)

#     # Method to get time series data for commodities over a specified date range.
#     # It validates the input symbols and date range before making the request.
#     def get_time_series(self, symbols: List[str], start_date: str, end_date: str) -> dict:
#         if not validate_symbols(symbols):
#             raise ValueError("Invalid symbols.")
#         if not validate_date(start_date) or not validate_date(end_date):
#             raise ValueError("Invalid date range.")

#         params = {
#             "symbols": ", ".join(symbols),
#             "startDate": start_date,
#             "endDate": end_date
#         }
#         url = f"https://api.apifreaks.com/v1.0/commodity/time-series?{urllib.parse.urlencode(params)}"
#         return self._make_request(url)

#     # Method to get a list of available commodity symbols.
#     # This method does not require any parameters and returns all available symbols.
#     def get_symbols(self) -> dict:
#         url = "https://api.apifreaks.com/v1.0/commodity/symbols"
#         return self._make_request(url)
