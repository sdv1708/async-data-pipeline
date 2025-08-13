from typing import Dict, Any
from app.cache.redis_client import redis_cache
from app.common.logging import get_logger
import random

logger = get_logger(__name__)

class EventEnricher:
    @staticmethod
    async def enrich_user_data(user_id: str) -> Dict[str, Any]:
        """
        Enriches user data with additional information.

        Args:
            user_id (str): The ID of the user.

        Returns:
            Dict[str, Any]: A dictionary containing the enriched user data.
        """
        # Check cache
        cache_key = f"user:{user_id}"
        cached = await redis_cache.get(cache_key)

        if cached:
            logger.info(f"Cache hit for user {user_id}")
            return cached

        # Simulate fetching from external service
        user_data = {
            "user_id": user_id,
            "segment": random.choice(["premium", "standard", "free"]),
            "lifetime_value": round(random.uniform(100, 10000), 2),
            "risk_score": round(random.uniform(0, 1), 2)
        }

        await redis_cache.set(cache_key, user_data, ttl=3600)

        logger.info(f"Cache miss for user {user_id}")
        return user_data
    
    @staticmethod
    async def enrich_product_data(sku: str) -> Dict[str, Any]:
        """
        Enriches product data with additional information.

        Args:
            sku (str): The SKU of the product.

        Returns:
            Dict[str, Any]: A dictionary containing the enriched product data.
        """
        # Check cache
        cache_key = f"product:{sku}"
        cached = await redis_cache.get(cache_key)

        if cached:
            logger.info(f"Cache hit for product {sku}")
            return cached
        
        # Simulate fetching from external service
        product_data = {
            "sku": sku,
            "category": random.choice(["electronics", "clothing", "books"]),
            "name": f"Product {sku}",
            "weight": round(random.uniform(0.1, 10), 2),
            "warehouse":  random.choice(["WH1", "WH2", "WH3"])
        }

        await redis_cache.set(cache_key, product_data, ttl=3600)
        return product_data

    @staticmethod 
    async def enrich_order_created_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches ORDER_CREATED event data with additional information.

        Args:
            event_data (Dict[str, Any]): The event data.

        Returns:
            Dict[str, Any]: A dictionary containing the enriched event data.
        """
        payload = event_data.get("payload", {})

        user_id = payload.get("user_id")
        if user_id:
            user_data = await EventEnricher.enrich_user_data(user_id)
            payload['user_enrichment'] = user_data

        items = payload.get("items", [])
        for item in items:
            sku = item.get("sku")
            if sku:
                product_data = await EventEnricher.enrich_product_data(sku)
                item['product_enrichment'] = product_data
        
        event['payload'] = payload
        event['enriched'] = True

        return event
