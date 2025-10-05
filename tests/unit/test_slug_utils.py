"""
Unit tests for slug utilities.

Tests slug generation and cleaning functionality.
"""
import pytest
from datetime import date
from core.slug_utils import clean_text_for_slug, generate_jam_slug, make_slug_unique


class TestSlugUtils:
    """Test cases for slug utility functions."""
    
    def test_clean_text_for_slug_basic(self) -> None:
        """Test basic text cleaning for slugs."""
        assert clean_text_for_slug("Hello World") == "hello-world"
        assert clean_text_for_slug("Test & More") == "test-more"
        assert clean_text_for_slug("Special@Characters!") == "specialcharacters"
    
    def test_clean_text_for_slug_edge_cases(self) -> None:
        """Test edge cases for text cleaning."""
        assert clean_text_for_slug("") == ""
        assert clean_text_for_slug("   ") == ""
        assert clean_text_for_slug("Multiple   Spaces") == "multiple-spaces"
        assert clean_text_for_slug("---Leading---Trailing---") == "leading-trailing"
    
    def test_clean_text_for_slug_special_characters(self) -> None:
        """Test handling of special characters."""
        assert clean_text_for_slug("Café & Bar") == "café-bar"
        assert clean_text_for_slug("Rock 'n' Roll") == "rock-n-roll"
        assert clean_text_for_slug("100% Pure") == "100-pure"
    
    def test_generate_jam_slug_name_only(self) -> None:
        """Test generating slug with name only."""
        result = generate_jam_slug("Friday Night Jam")
        assert result == "friday-night-jam"
    
    def test_generate_jam_slug_with_location(self) -> None:
        """Test generating slug with name and location."""
        result = generate_jam_slug("Friday Night Jam", "The Underground")
        assert result == "friday-night-jam-the-underground"
    
    def test_generate_jam_slug_with_date(self) -> None:
        """Test generating slug with name and date."""
        jam_date = date(2025, 10, 5)
        result = generate_jam_slug("Friday Night Jam", jam_date=jam_date)
        assert result == "friday-night-jam-2025-10-05"
    
    def test_generate_jam_slug_complete(self) -> None:
        """Test generating slug with all components."""
        jam_date = date(2025, 10, 5)
        result = generate_jam_slug("Friday Night Jam", "The Underground", jam_date)
        assert result == "friday-night-jam-the-underground-2025-10-05"
    
    def test_generate_jam_slug_empty_location(self) -> None:
        """Test generating slug with empty location."""
        jam_date = date(2025, 10, 5)
        result = generate_jam_slug("Friday Night Jam", "", jam_date)
        assert result == "friday-night-jam-2025-10-05"
    
    def test_make_slug_unique_new_slug(self) -> None:
        """Test making a unique slug when slug doesn't exist."""
        existing_slugs = ["existing-slug", "another-slug"]
        result = make_slug_unique("new-slug", existing_slugs)
        assert result == "new-slug"
    
    def test_make_slug_unique_existing_slug(self) -> None:
        """Test making a unique slug when slug already exists."""
        existing_slugs = ["existing-slug", "another-slug"]
        result = make_slug_unique("existing-slug", existing_slugs)
        assert result == "existing-slug-1"
    
    def test_make_slug_unique_multiple_conflicts(self) -> None:
        """Test making a unique slug with multiple conflicts."""
        existing_slugs = ["test-slug", "test-slug-1", "test-slug-2"]
        result = make_slug_unique("test-slug", existing_slugs)
        assert result == "test-slug-3"
    
    def test_make_slug_unique_empty_list(self) -> None:
        """Test making a unique slug with empty existing list."""
        result = make_slug_unique("new-slug", [])
        assert result == "new-slug"


class TestSlugUtilsIntegration:
    """Integration tests for slug utilities."""
    
    def test_slug_generation_workflow(self) -> None:
        """Test complete slug generation workflow."""
        # Simulate creating multiple jams with similar names
        jam_date = date(2025, 10, 5)
        existing_slugs = []
        
        # First jam
        base_slug = generate_jam_slug("Friday Night Jam", "The Underground", jam_date)
        unique_slug = make_slug_unique(base_slug, existing_slugs)
        existing_slugs.append(unique_slug)
        assert unique_slug == "friday-night-jam-the-underground-2025-10-05"
        
        # Second jam with same name
        base_slug2 = generate_jam_slug("Friday Night Jam", "The Underground", jam_date)
        unique_slug2 = make_slug_unique(base_slug2, existing_slugs)
        existing_slugs.append(unique_slug2)
        assert unique_slug2 == "friday-night-jam-the-underground-2025-10-05-1"
        
        # Third jam with different location
        base_slug3 = generate_jam_slug("Friday Night Jam", "The Venue", jam_date)
        unique_slug3 = make_slug_unique(base_slug3, existing_slugs)
        assert unique_slug3 == "friday-night-jam-the-venue-2025-10-05"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__])
