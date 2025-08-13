# scripts/init_db.py
import asyncio
from app.db.database import init_db, engine
from app.db.models import OrderEvent, OrderState, ProcessingError
from sqlmodel import SQLModel
from app.common.logging import get_logger

logger = get_logger(__name__)

async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        # Drop all tables
        # await conn.run_sync(SQLModel.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
        
    logger.info("database_tables_created")

async def main():
    """Initialize the database"""
    await create_tables()
    await engine.dispose()
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(main())