# app/consumer/processors/fraud.py
from typing import Dict, Any, List
from app.cache.redis_client import redis_cache
from app.common.logging import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)

class FraudDetector:
    """Detect potential fraud in orders"""
    
    @staticmethod
    async def check_velocity(user_id: str, amount: float) -> Dict[str, Any]:
        """Check for velocity-based fraud"""
        
        # Track order velocity
        key = f"velocity:{user_id}"
        now = datetime.now().timestamp()
        
        # Add current order
        await redis_cache.client.zadd(key, {str(now): now})
        
        # Count orders in last hour
        one_hour_ago = now - 3600
        recent_count = await redis_cache.client.zcount(key, one_hour_ago, now)
        
        # Clean old entries
        await redis_cache.client.zremrangebyscore(key, 0, one_hour_ago)
        await redis_cache.client.expire(key, 3600)
        
        # Flag if too many orders
        is_suspicious = recent_count > 5
        
        return {
            "check": "velocity",
            "suspicious": is_suspicious,
            "recent_orders": int(recent_count),
            "threshold": 5
        }
    
    @staticmethod
    async def check_amount_threshold(amount: float) -> Dict[str, Any]:
        """Check for abnormal amounts"""
        
        is_suspicious = amount > 5000
        
        return {
            "check": "amount_threshold",
            "suspicious": is_suspicious,
            "amount": amount,
            "threshold": 5000
        }
    
    @staticmethod
    async def check_user_risk(user_enrichment: Dict[str, Any]) -> Dict[str, Any]:
        """Check user risk score"""
        
        risk_score = user_enrichment.get('risk_score', 0)
        is_suspicious = risk_score > 0.7
        
        return {
            "check": "user_risk",
            "suspicious": is_suspicious,
            "risk_score": risk_score,
            "threshold": 0.7
        }
    
    @staticmethod
    async def analyze_order(event: Dict[str, Any]) -> Dict[str, Any]:
        """Run fraud analysis on order"""
        
        if event.get('event_type') != 'ORDER_CREATED':
            return {"fraud_checks": [], "is_fraudulent": False}
        
        payload = event.get('payload', {})
        user_id = payload.get('user_id')
        amount = payload.get('total_amount', 0)
        user_enrichment = payload.get('user_enrichment', {})
        
        checks = []
        
        # Run various fraud checks
        if user_id:
            velocity_check = await FraudDetector.check_velocity(user_id, amount)
            checks.append(velocity_check)
        
        amount_check = await FraudDetector.check_amount_threshold(amount)
        checks.append(amount_check)
        
        if user_enrichment:
            risk_check = await FraudDetector.check_user_risk(user_enrichment)
            checks.append(risk_check)
        
        # Determine if fraudulent
        is_fraudulent = any(check.get('suspicious', False) for check in checks)
        
        result = {
            "fraud_checks": checks,
            "is_fraudulent": is_fraudulent,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if is_fraudulent:
            logger.warning(
                "fraud_detected",
                order_id=event.get('order_id'),
                user_id=user_id,
                checks=checks
            )
            
            # Cache fraud flag
            await redis_cache.set(
                f"fraud:{event.get('order_id')}",
                result,
                ttl=86400  # 24 hours
            )
        
        return result