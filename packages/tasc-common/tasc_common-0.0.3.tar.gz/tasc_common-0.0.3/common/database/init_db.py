from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine

async def init_db(base_url: str, db_name: str):
    # Create a temporary engine to connect to 'postgres' database
    temp_engine = create_async_engine(f"{base_url}/{db_name}")
    
    async with temp_engine.begin() as conn:
        # Check if the database exists
        result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
        exists = result.scalar() == 1

        if not exists:
            # Create the database if it doesn't exist
            await conn.execute(text(f"CREATE DATABASE \"{db_name}\""))
            print(f"Database {db_name} created.")
        else:
            print(f"Database {db_name} already exists.")

# argparse
if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(description="Initialize the database.")
    parser.add_argument("--base_url", type=str, required=True, help="Base URL of the database.")
    parser.add_argument("--db_name", type=str, required=True, help="Name of the database to initialize.")
    args = parser.parse_args()
    asyncio.run(init_db(args.base_url, args.db_name))

