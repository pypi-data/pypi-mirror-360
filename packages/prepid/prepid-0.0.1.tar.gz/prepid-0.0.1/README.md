# Prebid Currency Converter

A Python package for fetching and converting currency rates using the Prebid currency file. The library provides a simple interface to convert amounts between different currencies, with automatic caching of currency data to minimize API requests.

## Installation

You can install the package from PyPI:

```bash
pip install prepid
```

## Usage

Here's a quick example of how to use the `CurrencyConverter` to convert 100 USD to EUR:

```python
from prepid import CurrencyConverter

# Initialize the converter
converter = CurrencyConverter()

# Convert 100 USD to EUR
try:
    converted_amount = converter.convert_currency(100, 'USD', 'EUR')
    print(f"100 USD is equal to {converted_amount:.2f} EUR")
except (ValueError, Exception) as e:
    print(f"Error: {e}")

# List all available currencies
try:
    available_currencies = converter.list_available_currencies()
    print("\nAvailable currencies:")
    print(', '.join(available_currencies))
except Exception as e:
    print(f"Error fetching currency list: {e}")
```

## Caching

The library automatically caches the currency data to avoid fetching it from the API on every request. By default, the cache expires after 6 hours. You can configure the cache duration when you initialize the `CurrencyConverter`:

```python
# Set cache to expire after 24 hours
converter = CurrencyConverter(cache_duration_hours=24)
```

The cache is stored in a user-specific directory, so it won't clutter your project folder.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on the [GitHub repository](https://github.com/kokamkarsahil/prepid-py/issues).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
