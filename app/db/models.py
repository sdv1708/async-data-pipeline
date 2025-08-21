from typing import Optional

from sqlmodel import Field, SQLModel


class OrderEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str
    order_id: str
    payload: str

    @staticmethod
    def from_event(event: dict) -> "OrderEvent":
        return OrderEvent(event_id=event["event_id"], order_id=event["order_id"], payload=str(event))
