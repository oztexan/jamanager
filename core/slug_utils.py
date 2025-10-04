"""
Slug Generation Utilities

This module handles generating user-friendly slugs for jams.
"""

import re
from datetime import date
from typing import Optional
from core.jam_config import JamConfig

def clean_text_for_slug(text: str) -> str:
    """Clean text to make it suitable for a URL slug"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text

def generate_jam_slug(name: str, location: Optional[str] = None, jam_date: Optional[date] = None) -> str:
    """Generate a user-friendly slug for a jam in format: name-location-date"""
    
    # Clean the name
    slug_parts = [clean_text_for_slug(name)]
    
    # Add location if provided
    if location and location.strip():
        slug_parts.append(clean_text_for_slug(location))
    
    # Add date if provided
    if jam_date:
        # Format date as YYYY-MM-DD
        date_str = jam_date.strftime("%Y-%m-%d")
        slug_parts.append(date_str)
    
    # Join parts with hyphens
    slug = "-".join(slug_parts)
    
    # Ensure slug doesn't exceed max length
    if len(slug) > JamConfig.MAX_SLUG_LENGTH:
        # Truncate and remove any partial words
        slug = slug[:JamConfig.MAX_SLUG_LENGTH]
        slug = slug.rsplit('-', 1)[0]  # Remove last partial word
    
    return slug

def make_slug_unique(base_slug: str, existing_slugs: list[str]) -> str:
    """Make a slug unique by appending a number if necessary"""
    if base_slug not in existing_slugs:
        return base_slug
    
    counter = 1
    while f"{base_slug}-{counter}" in existing_slugs:
        counter += 1
    
    return f"{base_slug}-{counter}"
