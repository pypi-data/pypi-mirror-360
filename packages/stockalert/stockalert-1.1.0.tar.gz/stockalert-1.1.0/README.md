# StockAlert.pro Python SDK

Official Python SDK for the StockAlert.pro API.

## Installation

```bash
pip install stockalert
```

## Quick Start

```python
from stockalert import StockAlert

# Initialize the client
client = StockAlert(api_key="sk_your_api_key")

# List all alerts
alerts = client.alerts.list()

# Create a new alert
alert = client.alerts.create(
    symbol="AAPL",
    condition="price_above",
    threshold=200,
    notification="email"
)

# Update alert status
client.alerts.update(alert.id, status="paused")

# Delete alert
client.alerts.delete(alert.id)
```

## Features

- 🐍 Python 3.7+ support
- 🔄 Automatic retries with exponential backoff
- 🛡️ Type hints for better IDE support
- 📦 Minimal dependencies
- 🧪 Comprehensive test suite
- 📚 Detailed documentation

## Async Support

The SDK also supports async operations:

```python
import asyncio
from stockalert import AsyncStockAlert

async def main():
    async with AsyncStockAlert(api_key="sk_your_api_key") as client:
        alerts = await client.alerts.list()
        print(f"Found {len(alerts.data)} alerts")

asyncio.run(main())
```

## Documentation

Full documentation is available at [https://stockalert.pro/api/docs](https://stockalert.pro/api/docs)

## License

MIT