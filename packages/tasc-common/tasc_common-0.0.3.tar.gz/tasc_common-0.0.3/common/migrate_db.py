import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from alembic.config import Config
from alembic import command
from sqlalchemy import text

from common.config import common_settings

async def wait_for_db():
    """Wait for the database to be ready."""
    engine = create_async_engine(str(common_settings.DATABASE_URL))
    max_retries = 5
    retry_interval = 5
    for _ in range(max_retries):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("Database is ready!")
            return True
        except Exception as e:
            print(f"Database not ready yet: {e}")
            await asyncio.sleep(retry_interval)

    print("Failed to connect to the database after multiple attempts")
    return False

async def run_migrations():
    """Run database migrations using Alembic."""
    if await wait_for_db():
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully!")
    else:
        print("Failed to run migrations due to database connection issues")

if __name__ == "__main__":
    asyncio.run(run_migrations())
