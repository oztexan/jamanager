"""
Connection Pool Management for Sprint 3 Architecture Improvements
Provides advanced connection pooling and database session management.
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

from core.config import get_config

logger = logging.getLogger(__name__)

class ConnectionPoolManager:
    """Manages database connection pools with monitoring and optimization."""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._config = get_config()
        self._connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "idle_connections": 0,
            "failed_connections": 0,
            "slow_queries": 0
        }
        self._slow_query_threshold = self._config.performance.slow_query_threshold
    
    def initialize(self) -> None:
        """Initialize the connection pool."""
        if self._engine is not None:
            logger.warning("Connection pool already initialized")
            return
        
        # Determine pool class based on database type
        if "sqlite" in self._config.database.url:
            # SQLite doesn't support connection pooling, use StaticPool
            pool_class = StaticPool
            pool_kwargs = {
                "connect_args": {"check_same_thread": False},
                "pool_pre_ping": True
            }
        else:
            # Use QueuePool for other databases
            pool_class = QueuePool
            pool_kwargs = {
                "pool_size": self._config.database.pool_size,
                "max_overflow": self._config.database.max_overflow,
                "pool_timeout": self._config.database.pool_timeout,
                "pool_recycle": self._config.database.pool_recycle,
                "pool_pre_ping": True
            }
        
        # Create engine with connection pooling
        self._engine = create_async_engine(
            self._config.database.url,
            echo=self._config.database.echo,
            poolclass=pool_class,
            **pool_kwargs
        )
        
        # Create session factory
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Add event listeners for monitoring
        self._setup_event_listeners()
        
        logger.info(f"Connection pool initialized with {pool_class.__name__}")
        logger.info(f"Pool size: {self._config.database.pool_size}, Max overflow: {self._config.database.max_overflow}")
    
    def _setup_event_listeners(self) -> None:
        """Setup event listeners for connection monitoring."""
        
        @event.listens_for(self._engine.sync_engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            """Called when a new connection is created."""
            self._connection_stats["total_connections"] += 1
            logger.debug("New database connection created")
        
        @event.listens_for(self._engine.sync_engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """Called when a connection is checked out from the pool."""
            self._connection_stats["active_connections"] += 1
            if self._connection_stats["idle_connections"] > 0:
                self._connection_stats["idle_connections"] -= 1
            logger.debug("Database connection checked out")
        
        @event.listens_for(self._engine.sync_engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            """Called when a connection is returned to the pool."""
            if self._connection_stats["active_connections"] > 0:
                self._connection_stats["active_connections"] -= 1
            self._connection_stats["idle_connections"] += 1
            logger.debug("Database connection checked in")
        
        @event.listens_for(self._engine.sync_engine, "invalidate")
        def on_invalidate(dbapi_connection, connection_record, exception):
            """Called when a connection is invalidated."""
            self._connection_stats["failed_connections"] += 1
            logger.warning(f"Database connection invalidated: {exception}")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session from the pool."""
        if self._session_factory is None:
            raise RuntimeError("Connection pool not initialized")
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with context manager."""
        if self._session_factory is None:
            raise RuntimeError("Connection pool not initialized")
        
        session = self._session_factory()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
    
    async def execute_with_timing(self, session: AsyncSession, query, *args, **kwargs):
        """Execute a query with timing and slow query detection."""
        start_time = time.time()
        
        try:
            result = await session.execute(query, *args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > self._slow_query_threshold:
                self._connection_stats["slow_queries"] += 1
                logger.warning(f"Slow query detected: {execution_time:.3f}s - {query}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query failed after {execution_time:.3f}s: {e}")
            raise
    
    def get_connection_stats(self) -> dict:
        """Get current connection pool statistics."""
        if self._engine is None:
            return {"error": "Connection pool not initialized"}
        
        pool = self._engine.pool
        stats = self._connection_stats.copy()
        
        # Add pool-specific stats
        stats.update({
            "pool_size": pool.size(),
            "checked_in_connections": pool.checkedin(),
            "checked_out_connections": pool.checkedout(),
            "overflow_connections": pool.overflow(),
            "invalid_connections": pool.invalid()
        })
        
        return stats
    
    async def health_check(self) -> dict:
        """Perform a health check on the connection pool."""
        if self._engine is None:
            return {"status": "error", "message": "Connection pool not initialized"}
        
        try:
            # Test connection
            async with self.get_session() as session:
                await session.execute("SELECT 1")
            
            stats = self.get_connection_stats()
            
            # Check for issues
            issues = []
            if stats.get("failed_connections", 0) > 10:
                issues.append("High number of failed connections")
            
            if stats.get("slow_queries", 0) > 50:
                issues.append("High number of slow queries")
            
            if stats.get("checked_out_connections", 0) > stats.get("pool_size", 0) * 0.8:
                issues.append("High connection pool utilization")
            
            status = "healthy" if not issues else "degraded"
            
            return {
                "status": status,
                "issues": issues,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Connection pool health check failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "stats": self.get_connection_stats()
            }
    
    async def close(self) -> None:
        """Close the connection pool."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Connection pool closed")

# Global connection pool manager
connection_pool = ConnectionPoolManager()

# Convenience functions
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session from the global connection pool."""
    async for session in connection_pool.get_session():
        yield session

@asynccontextmanager
async def get_database_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with context manager."""
    async with connection_pool.get_session_context() as session:
        yield session

async def execute_with_timing(session: AsyncSession, query, *args, **kwargs):
    """Execute a query with timing and slow query detection."""
    return await connection_pool.execute_with_timing(session, query, *args, **kwargs)

def get_connection_stats() -> dict:
    """Get current connection pool statistics."""
    return connection_pool.get_connection_stats()

async def health_check() -> dict:
    """Perform a health check on the connection pool."""
    return await connection_pool.health_check()

# Initialize connection pool
def initialize_connection_pool() -> None:
    """Initialize the global connection pool."""
    connection_pool.initialize()

# Cleanup function
async def cleanup_connection_pool() -> None:
    """Cleanup the global connection pool."""
    await connection_pool.close()
