import pytest
import requests_mock
from datetime import timedelta
import os
import json
from prepid import CurrencyConverter, CurrencyError


@pytest.fixture
def mock_api_response():
    return {
        "conversions": {
            "publicationDate": 1672531200000,
            "rates": {"USD": {"rate": 1.0}, "EUR": {"rate": 0.9}, "GBP": {"rate": 0.8}},
        }
    }


@pytest.fixture
def converter(tmp_path):
    # Override the cache directory to use a temporary path for tests
    converter = CurrencyConverter()
    converter.cache_dir = str(tmp_path)
    converter.cache_file = os.path.join(converter.cache_dir, "currency_cache.json")
    return converter


def test_convert_currency(converter, mock_api_response):
    with requests_mock.Mocker() as m:
        m.get(converter.currency_api_url, json=mock_api_response)

        amount = converter.convert_currency(100, "USD", "EUR")
        assert amount == 90.0


def test_list_available_currencies(converter, mock_api_response):
    with requests_mock.Mocker() as m:
        m.get(converter.currency_api_url, json=mock_api_response)

        currencies = converter.list_available_currencies()
        assert sorted(currencies) == sorted(["USD", "EUR", "GBP"])


def test_caching(converter, mock_api_response):
    with requests_mock.Mocker() as m:
        m.get(converter.currency_api_url, json=mock_api_response)

        # First call should fetch from API
        converter.get_currency_rates()
        assert m.called
        assert m.call_count == 1

        # Second call should use cache
        converter.get_currency_rates()
        assert m.call_count == 1


def test_cache_expiration(converter, mock_api_response):
    with requests_mock.Mocker() as m:
        m.get(converter.currency_api_url, json=mock_api_response)

        # Set a short cache duration for testing
        converter.cache_duration = timedelta(seconds=-1)  # Expired

        # First call
        converter.get_currency_rates()
        assert m.call_count == 1

        # Second call should also fetch from API because cache is expired
        converter.get_currency_rates()
        assert m.call_count == 2


def test_invalid_currency(converter, mock_api_response):
    with requests_mock.Mocker() as m:
        m.get(converter.currency_api_url, json=mock_api_response)

        with pytest.raises(CurrencyError, match="Invalid currency code provided."):
            converter.convert_currency(100, "USD", "XYZ")


def test_api_error(converter):
    with requests_mock.Mocker() as m:
        m.get(converter.currency_api_url, status_code=500)

        with pytest.raises(CurrencyError, match="Failed to fetch currency data"):
            converter.get_currency_rates()


def test_init_with_custom_cache_duration():
    converter = CurrencyConverter(cache_duration_hours=10)
    assert converter.cache_duration == timedelta(hours=10)


def test_corrupt_cache(converter, mock_api_response):
    # Create a corrupt cache file
    with open(converter.cache_file, "w") as f:
        f.write("corrupt data")

    with requests_mock.Mocker() as m:
        m.get(converter.currency_api_url, json=mock_api_response)

        # Should fetch from API since cache is corrupt and replace the cache file
        rates = converter.get_currency_rates()
        assert m.called
        assert os.path.exists(converter.cache_file)

        # Verify the new cache file is valid
        with open(converter.cache_file, "r") as f:
            cached_content = json.load(f)
        assert cached_content["data"] == mock_api_response
        assert rates == mock_api_response


def test_convert_same_currency(converter):
    assert converter.convert_currency(100, "USD", "USD") == 100


def test_in_memory_cache(converter, mock_api_response):
    with requests_mock.Mocker() as m:
        m.get(converter.currency_api_url, json=mock_api_response)

        # First call fetches and caches in memory
        converter.get_currency_rates()
        assert m.call_count == 1

        # Second call should use in-memory cache, not API
        converter.get_currency_rates()
        assert m.call_count == 1
