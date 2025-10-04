#!/usr/bin/env python3
"""
Reset development database with popular songs
This script resets the database and initializes it with the default dev song set
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from init_dev_database import init_dev_database

async def reset_dev_database() -> None:
    """Reset and initialize development database"""
    print("🔄 Resetting development database...")
    await init_dev_database()
    print("✅ Development database reset complete!")

if __name__ == "__main__":
    asyncio.run(reset_dev_database())
