"""Async alerts resource."""
from typing import Any, AsyncGenerator, Dict

from ..exceptions import ValidationError
from ..types import Alert, AlertStatus
from .alerts_base import AlertsResourceBase


class AsyncAlertsResource(AlertsResourceBase):
    """Async alerts resource."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self._config = config
        self.client: Any = None  # Set by AsyncStockAlert

    async def list(self, **params: Any) -> Dict[str, Any]:
        """List alerts with optional filtering."""
        if "symbol" in params:
            params["symbol"] = str(params["symbol"]).upper()

        response = await self.client._request("GET", "/alerts", params=params)
        return response  # type: ignore[no-any-return]

    async def create(self, **data: Any) -> Alert:
        """Create a new alert."""
        if "notification" not in data:
            data["notification"] = "email"

        self._validate_create_request(data)
        response = await self.client._request("POST", "/alerts", json=data)
        return Alert(response)

    async def get(self, alert_id: str) -> Alert:
        """Get alert by ID."""
        if not alert_id:
            raise ValidationError("Alert ID is required")

        response = await self.client._request("GET", f"/alerts/{alert_id}")
        return Alert(response)

    async def update(self, alert_id: str, status: AlertStatus) -> Alert:
        """Update alert status."""
        if not alert_id:
            raise ValidationError("Alert ID is required")

        if status not in ["active", "paused"]:
            raise ValidationError('Status must be either "active" or "paused"')

        response = await self.client._request("PUT", f"/alerts/{alert_id}", json={"status": status})
        return Alert(response)

    async def delete(self, alert_id: str) -> Dict[str, Any]:
        """Delete an alert."""
        if not alert_id:
            raise ValidationError("Alert ID is required")

        return await self.client._request("DELETE", f"/alerts/{alert_id}")

    async def iterate(self, **params: Any) -> AsyncGenerator[Alert, None]:
        """Iterate through all alerts with automatic pagination."""
        offset = 0
        limit = min(params.get("limit", 100), 100)

        base_params = {k: v for k, v in params.items() if k not in ["limit", "offset"]}

        while True:
            page = await self.list(**base_params, limit=limit, offset=offset)

            if "data" in page:
                for alert_data in page["data"]:
                    yield Alert(alert_data)

                if len(page["data"]) < limit:
                    break
            else:
                break

            offset += limit
