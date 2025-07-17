# Database Configuration for Hospital Supply System

import os
from urllib.parse import quote_plus

# PostgreSQL Database Configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "hospital_supply_db",
    "username": "postgres",
    "password": os.getenv("POSTGRES_PASSWORD", ""),  # Will prompt if not set
}

# Connection string for SQLAlchemy (sync)
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{quote_plus(DATABASE_CONFIG['password'])}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# Async connection string for SQLAlchemy
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DATABASE_CONFIG['username']}:{quote_plus(DATABASE_CONFIG['password'])}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# Connection Pool Settings
POOL_SETTINGS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True,
}

# Async Pool Settings
ASYNC_POOL_SETTINGS = {
    "min_size": 5,
    "max_size": 20,
    "max_inactive_connection_lifetime": 3600,
}

print("Database configuration loaded:")
print(f"Host: {DATABASE_CONFIG['host']}")
print(f"Port: {DATABASE_CONFIG['port']}")
print(f"Database: {DATABASE_CONFIG['database']}")
print(f"Username: {DATABASE_CONFIG['username']}")
print("✅ Ready for connection!")
