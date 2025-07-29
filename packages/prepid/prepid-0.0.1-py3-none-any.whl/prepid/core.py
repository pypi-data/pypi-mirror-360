import json
import os
from datetime import datetime, timedelta
import requests
from appdirs import user_cache_dir


class CurrencyError(Exception):
    """Custom exception for currency conversion errors."""

    pass


class CurrencyConverter:
    def __init__(self, cache_duration_hours=6):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.currency_api_url = (
            "https://cdn.jsdelivr.net/gh/prebid/currency-file@1/latest.json"
        )
        self._rates_data = None
        self._rates_data_expiry = None

        # Setup cache directory
        self.cache_dir = user_cache_dir("prepid", "prebid-currency")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, "currency_cache.json")

    def _get_cached_data(self):
        """Get cached currency data if it exists and is not expired."""
        if not os.path.exists(self.cache_file):
            return None, None

        try:
            with open(self.cache_file, "r") as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache["cached_at"])

                if datetime.now() - cache_time < self.cache_duration:
                    expiry = cache_time + self.cache_duration
                    return cache["data"], expiry
        except (json.JSONDecodeError, KeyError, ValueError):
            # Cache is invalid, remove it
            os.remove(self.cache_file)

        return None, None

    def _save_to_cache(self, data):
        """Save currency data to cache with current timestamp."""
        cache = {"cached_at": datetime.now().isoformat(), "data": data}
        with open(self.cache_file, "w") as f:
            json.dump(cache, f)

    def _fetch_currency_data(self):
        """Fetch latest currency data from the API."""
        try:
            response = requests.get(self.currency_api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            self._save_to_cache(data)
            return data
        except (requests.RequestException, json.JSONDecodeError) as e:
            raise CurrencyError(f"Failed to fetch currency data: {str(e)}")

    def get_currency_rates(self):
        """Get currency rates, using cache if available and not expired."""
        if (
            self._rates_data is not None
            and self._rates_data_expiry
            and datetime.now() < self._rates_data_expiry
        ):
            return self._rates_data

        cached_data, expiry = self._get_cached_data()
        if cached_data is not None:
            self._rates_data = cached_data
            self._rates_data_expiry = expiry
            return self._rates_data

        self._rates_data = self._fetch_currency_data()
        self._rates_data_expiry = datetime.now() + self.cache_duration
        return self._rates_data

    def list_available_currencies(self):
        """List all available currency codes in the data."""
        data = self.get_currency_rates()
        return list(data["conversions"]["rates"].keys())

    def get_conversion_rate(self, from_currency, to_currency):
        """Get the conversion rate between two currencies."""
        data = self.get_currency_rates()
        rates = data["conversions"]["rates"]

        if from_currency not in rates or to_currency not in rates:
            raise CurrencyError("Invalid currency code provided.")

        from_rate = rates[from_currency]["rate"]
        to_rate = rates[to_currency]["rate"]

        return to_rate / from_rate

    def convert_currency(self, amount, from_currency, to_currency):
        """Convert an amount from one currency to another."""
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")

        if from_currency == to_currency:
            return amount

        rate = self.get_conversion_rate(from_currency, to_currency)
        return amount * rate
