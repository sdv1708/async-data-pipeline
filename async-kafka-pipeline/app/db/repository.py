# app/db/repository.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import select
from sqlalchemy.dialects.postgresql import insert
from app.db.models import OrderEvent, OrderState, ProcessingError
from app.db.database import get_session
from app.common.logging import get_logger

logger = get_logger(__name__)

class EventRepository:
    """Repository for event storage and retrieval"""
    
    @staticmethod
    async def save_event(
        event_id: str,
        event_type: str,
        order_id: str,
        timestamp: datetime,
        payload: Dict[str, Any],
        kafka_partition: Optional[int] = None,
        kafka_offset: Optional[int] = None,
        source: str = "synthetic"
    ) -> OrderEvent:
        """Save an event to the database (idempotent)"""
        
        async with get_session() as session:
            # Use INSERT ... ON CONFLICT DO NOTHING for idempotency
            stmt = insert(OrderEvent).values(
                event_id=event_id,
                event_type=event_type,
                order_id=order_id,
                timestamp=timestamp,
                payload=payload,
                kafka_partition=kafka_partition,
                kafka_offset=kafka_offset,
                source=source,
                processed_at=datetime.utcnow()
            )
            
            # On conflict, do nothing (event already processed)
            stmt = stmt.on_conflict_do_nothing(index_elements=['event_id'])
            
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount == 0:
                logger.warning("event_already_exists", event_id=event_id)
            else:
                logger.info("event_saved", event_id=event_id, order_id=order_id)
            
            # Fetch and return the event
            query = select(OrderEvent).where(OrderEvent.event_id == event_id)
            event = await session.execute(query)
            return event.scalar_one()
    
    @staticmethod
    async def update_order_state(event: Dict[str, Any]) -> OrderState:
        """Update order state based on event"""
        
        async with get_session() as session:
            order_id = event['order_id']
            event_type = event['event_type']
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            
            # Get or create order state
            query = select(OrderState).where(OrderState.order_id == order_id)
            result = await session.execute(query)
            order_state = result.scalar_one_or_none()
            
            if not order_state:
                order_state = OrderState(order_id=order_id)
                session.add(order_state)
            
            # Update based on event type
            if event_type == 'ORDER_CREATED':
                payload = event.get('payload', {})
                order_state.user_id = payload.get('user_id')
                order_state.total_amount = payload.get('total_amount')
                order_state.status = 'pending'
                order_state.created_at = timestamp
                
            elif event_type == 'PAYMENT_AUTHORIZED':
                order_state.status = 'paid'
                order_state.paid_at = timestamp
                
            elif event_type == 'ITEM_PICKED':
                order_state.status = 'picked'
                order_state.picked_at = timestamp
                
            elif event_type == 'SHIPMENT_DISPATCHED':
                order_state.status = 'shipped'
                order_state.shipped_at = timestamp
            
            # Update metadata
            order_state.updated_at = datetime.utcnow()
            order_state.version += 1
            
            await session.commit()
            
            logger.info(
                "order_state_updated",
                order_id=order_id,
                status=order_state.status,
                version=order_state.version
            )
            
            return order_state
    
    @staticmethod
    async def save_error(
        event: Dict[str, Any],
        error_type: str,
        error_message: str
    ) -> ProcessingError:
        """Save processing error for retry/analysis"""
        
        async with get_session() as session:
            error = ProcessingError(
                event_id=event.get('event_id'),
                order_id=event.get('order_id'),
                error_type=error_type,
                error_message=error_message,
                raw_event=event
            )
            
            session.add(error)
            await session.commit()
            
            logger.error(
                "processing_error_saved",
                event_id=error.event_id,
                error_type=error_type
            )
            
            return error