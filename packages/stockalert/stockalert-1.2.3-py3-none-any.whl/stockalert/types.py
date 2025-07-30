"""Type definitions for StockAlert SDK."""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

AlertCondition = Literal[
    "price_above",
    "price_below",
    "price_change_up",
    "price_change_down",
    "new_high",
    "new_low",
    "reminder",
    "daily_reminder",
    "ma_crossover_golden",
    "ma_crossover_death",
    "ma_touch_above",
    "ma_touch_below",
    "volume_change",
    "rsi_limit",
    "pe_ratio_below",
    "pe_ratio_above",
    "forward_pe_below",
    "forward_pe_above",
    "earnings_announcement",
    "dividend_ex_date",
    "dividend_payment"
]

# Notification channels - NO WhatsApp!
NotificationChannel = Literal["email", "sms"]

# Alert status
AlertStatus = Literal["active", "paused", "triggered"]

class Alert:
    """Alert object."""
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data["id"]
        self.symbol: str = data["symbol"]
        self.condition: AlertCondition = data["condition"]
        self.threshold: Optional[float] = data.get("threshold")
        self.notification: NotificationChannel = data["notification"]
        self.status: AlertStatus = data["status"]
        self.created_at: datetime = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
        self.updated_at: datetime = datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
        self.last_triggered: Optional[datetime] = None
        if data.get("last_triggered"):
            self.last_triggered = datetime.fromisoformat(data["last_triggered"].replace('Z', '+00:00'))
        self.initial_price: Optional[float] = data.get("initial_price")
        self.parameters: Optional[Dict[str, Any]] = data.get("parameters")
        self._raw_data = data

    def __repr__(self) -> str:
        return f"<Alert {self.id}: {self.symbol} {self.condition}>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self._raw_data

class PaginatedResponse:
    """Paginated response."""
    def __init__(self, data: List[Dict[str, Any]], meta: Dict[str, Any]):
        self.data = data
        self.meta = meta
        self.total = meta.get("total", 0)
        self.limit = meta.get("limit", 100)
        self.offset = meta.get("offset", 0)
        self.has_more = meta.get("has_more", False)

class WebhookPayload:
    """Webhook payload."""
    def __init__(self, data: Dict[str, Any]):
        self.event: str = data["event"]
        self.timestamp: datetime = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        self.data: Dict[str, Any] = data["data"]
        self._raw_data = data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self._raw_data

# API Response types
ApiResponse = Dict[str, Any]
