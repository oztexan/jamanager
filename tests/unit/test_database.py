"""
Unit tests for database module.

Tests database connection, session management, and initialization.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from core.database import get_database, get_database_url, init_database, AsyncSessionLocal


class TestDatabase:
    """Test cases for database functionality."""
    
    def test_get_database_url(self) -> None:
        """Test getting database URL."""
        url = get_database_url()
        assert isinstance(url, str)
        assert url is not None
        assert len(url) > 0
    
    @pytest.mark.asyncio
    async def test_get_database_session(self) -> None:
        """Test database session dependency."""
        session_count = 0
        
        async for session in get_database():
            session_count += 1
            assert session is not None
            # Only test one iteration to avoid infinite loop
            break
        
        assert session_count == 1
    
    @pytest.mark.asyncio
    async def test_init_database(self) -> None:
        """Test database initialization."""
        # Mock the engine and connection
        with patch('core.database.engine') as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn
            
            # Should not raise any exceptions
            await init_database()
            
            # Verify the connection was used
            mock_engine.begin.assert_called_once()
            mock_conn.run_sync.assert_called_once()


class TestDatabaseIntegration:
    """Integration tests for database functionality."""
    
    @pytest.mark.asyncio
    async def test_database_session_lifecycle(self) -> None:
        """Test that database sessions are properly closed."""
        # This test would require a real database connection
        # For now, we'll test the structure
        async for session in get_database():
            # Verify session is an AsyncSession
            assert hasattr(session, 'close')
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')
            break


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__])
