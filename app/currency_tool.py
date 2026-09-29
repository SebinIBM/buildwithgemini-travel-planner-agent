"""Minimal currency conversion tool for travel planning."""

import requests


def convert_travel_currency(
    amount: float, from_currency: str = "USD", to_currency: str = "JPY"
) -> str:
    """Convert a monetary budget amount between currencies (e.g. converting USD daily budget to JPY or EUR).

    Args:
        amount: The numerical amount to convert (e.g. 180).
        from_currency: Source 3-letter currency code (default: 'USD').
        to_currency: Target 3-letter currency code (default: 'JPY').

    Returns:
        A string summarizing the converted value and rate.
    """
    try:
        from_code = from_currency.upper().strip()
        to_code = to_currency.upper().strip()
        url = f"https://open.er-api.com/v6/latest/{from_code}"
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return f"Unable to fetch exchange rates for {from_code}."

        data = res.json()
        rates = data.get("rates", {})
        if to_code not in rates:
            return f"Currency '{to_code}' not supported."

        rate = rates[to_code]
        converted = amount * rate
        return f"{amount:.2f} {from_code} = {converted:.2f} {to_code} (Rate: 1 {from_code} = {rate:.4f} {to_code})"
    except Exception as e:
        return f"Error converting currency: {e}"
