"""
Unit tests for dev-info API endpoint.

Tests the /api/dev-info endpoint functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from api.endpoints.static import get_dev_info


class TestDevInfoAPI:
    """Test cases for dev-info API endpoint."""
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_get_dev_info_success(self, mock_run: MagicMock) -> None:
        """Test successful dev info retrieval."""
        # Mock git commands
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="feature/test-branch\n"),
            MagicMock(returncode=0, stdout="abc1234\n")
        ]
        
        result = await get_dev_info()
        
        assert "git_branch" in result
        assert "git_commit" in result
        assert "environment" in result
        
        assert result["git_branch"] == "feature/test-branch"
        assert result["git_commit"] == "abc1234"
        assert result["environment"] == "development"
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_get_dev_info_git_failure(self, mock_run: MagicMock) -> None:
        """Test dev info when git commands fail."""
        # Mock git commands to fail
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=""),
            MagicMock(returncode=1, stdout="")
        ]
        
        result = await get_dev_info()
        
        assert result["git_branch"] == "unknown"
        assert result["git_commit"] == "unknown"
        assert result["environment"] == "development"
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_get_dev_info_partial_failure(self, mock_run: MagicMock) -> None:
        """Test dev info when only one git command fails."""
        # Mock branch command to succeed, commit to fail
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="main\n"),
            MagicMock(returncode=1, stdout="")
        ]
        
        result = await get_dev_info()
        
        assert result["git_branch"] == "main"
        assert result["git_commit"] == "unknown"
        assert result["environment"] == "development"
    
    @pytest.mark.asyncio
    async def test_get_dev_info_exception_handling(self) -> None:
        """Test dev info when subprocess raises exception."""
        with patch('subprocess.run', side_effect=Exception("Git not found")):
            result = await get_dev_info()
            
            assert result["git_branch"] == "unknown"
            assert result["git_commit"] == "unknown"
            assert result["environment"] == "development"


class TestDevInfoAPIResponseFormat:
    """Test response format consistency."""
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_response_format(self, mock_run: MagicMock) -> None:
        """Test that response has consistent format."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="test-branch\n"),
            MagicMock(returncode=0, stdout="test123\n")
        ]
        
        result = await get_dev_info()
        
        # Check all required fields are present
        required_fields = ["git_branch", "git_commit", "environment"]
        for field in required_fields:
            assert field in result
            assert isinstance(result[field], str)
            assert len(result[field]) > 0 or result[field] == "unknown"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__])