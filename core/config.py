"""
Configuration Management for Sprint 3 Architecture Improvements
Provides centralized configuration management with environment variable support.
"""

import os
import logging
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/development/jamanager.db"))
    echo: bool = field(default_factory=lambda: os.getenv("DATABASE_ECHO", "true").lower() == "true")
    pool_size: int = field(default_factory=lambda: int(os.getenv("DATABASE_POOL_SIZE", "10")))
    max_overflow: int = field(default_factory=lambda: int(os.getenv("DATABASE_MAX_OVERFLOW", "20")))
    pool_timeout: int = field(default_factory=lambda: int(os.getenv("DATABASE_POOL_TIMEOUT", "30")))
    pool_recycle: int = field(default_factory=lambda: int(os.getenv("DATABASE_POOL_RECYCLE", "3600")))

@dataclass
class CacheConfig:
    """Cache configuration settings."""
    enabled: bool = field(default_factory=lambda: os.getenv("CACHE_ENABLED", "true").lower() == "true")
    default_ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_DEFAULT_TTL", "300")))
    max_size: int = field(default_factory=lambda: int(os.getenv("CACHE_MAX_SIZE", "1000")))
    cleanup_interval: int = field(default_factory=lambda: int(os.getenv("CACHE_CLEANUP_INTERVAL", "60")))

@dataclass
class WebSocketConfig:
    """WebSocket configuration settings."""
    enabled: bool = field(default_factory=lambda: os.getenv("WEBSOCKET_ENABLED", "true").lower() == "true")
    max_connections: int = field(default_factory=lambda: int(os.getenv("WEBSOCKET_MAX_CONNECTIONS", "100")))
    heartbeat_interval: int = field(default_factory=lambda: int(os.getenv("WEBSOCKET_HEARTBEAT_INTERVAL", "30")))
    connection_timeout: int = field(default_factory=lambda: int(os.getenv("WEBSOCKET_CONNECTION_TIMEOUT", "300")))

@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
    access_code: str = field(default_factory=lambda: os.getenv("JAM_MANAGER_ACCESS_CODE", "dev-access-code"))
    cors_origins: list = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(","))
    rate_limit_enabled: bool = field(default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true")
    rate_limit_requests: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_REQUESTS", "100")))
    rate_limit_window: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW", "60")))

@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    file_enabled: bool = field(default_factory=lambda: os.getenv("LOG_FILE_ENABLED", "false").lower() == "true")
    file_path: str = field(default_factory=lambda: os.getenv("LOG_FILE_PATH", "logs/app.log"))
    max_file_size: int = field(default_factory=lambda: int(os.getenv("LOG_MAX_FILE_SIZE", "10485760")))  # 10MB
    backup_count: int = field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", "5")))

@dataclass
class PerformanceConfig:
    """Performance configuration settings."""
    enable_profiling: bool = field(default_factory=lambda: os.getenv("ENABLE_PROFILING", "false").lower() == "true")
    slow_query_threshold: float = field(default_factory=lambda: float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0")))
    max_request_size: int = field(default_factory=lambda: int(os.getenv("MAX_REQUEST_SIZE", "16777216")))  # 16MB
    request_timeout: int = field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "30")))

@dataclass
class AppConfig:
    """Main application configuration."""
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "true").lower() == "true")
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    reload: bool = field(default_factory=lambda: os.getenv("RELOAD", "true").lower() == "true")
    workers: int = field(default_factory=lambda: int(os.getenv("WORKERS", "1")))
    
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    websocket: WebSocketConfig = field(default_factory=WebSocketConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

class ConfigManager:
    """Manages application configuration with runtime updates."""
    
    def __init__(self, config_file: Optional[str] = None):
        self._config = AppConfig()
        self._config_file = config_file
        self._watchers: list = []
        
        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)
    
    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration at runtime."""
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                logger.info(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown config key: {key}")
        
        # Notify watchers
        for watcher in self._watchers:
            try:
                watcher(self._config)
            except Exception as e:
                logger.error(f"Error in config watcher: {e}")
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from a JSON file."""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update configuration with file data
            self.update_config(config_data)
            logger.info(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
    
    def save_to_file(self, config_file: str) -> None:
        """Save current configuration to a JSON file."""
        try:
            config_dict = self._config_to_dict()
            
            # Ensure directory exists
            Path(config_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Saved configuration to {config_file}")
            
        except Exception as e:
            logger.error(f"Error saving config file {config_file}: {e}")
    
    def add_watcher(self, watcher: callable) -> None:
        """Add a configuration change watcher."""
        self._watchers.append(watcher)
    
    def remove_watcher(self, watcher: callable) -> None:
        """Remove a configuration change watcher."""
        if watcher in self._watchers:
            self._watchers.remove(watcher)
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = {}
        
        for field_name, field_value in self._config.__dict__.items():
            if hasattr(field_value, '__dict__'):
                # Handle dataclass fields
                config_dict[field_name] = field_value.__dict__
            else:
                config_dict[field_name] = field_value
        
        return config_dict
    
    def get_database_url(self) -> str:
        """Get the database URL."""
        return self._config.database.url
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self._config.environment.lower() == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self._config.environment.lower() == "production"
    
    def get_cors_origins(self) -> list:
        """Get CORS origins."""
        return self._config.security.cors_origins
    
    def get_log_level(self) -> str:
        """Get logging level."""
        return self._config.logging.level

# Global configuration manager instance
config_manager = ConfigManager()

# Convenience functions
def get_config() -> AppConfig:
    """Get the current application configuration."""
    return config_manager.get_config()

def get_database_url() -> str:
    """Get the database URL."""
    return config_manager.get_database_url()

def is_development() -> bool:
    """Check if running in development mode."""
    return config_manager.is_development()

def is_production() -> bool:
    """Check if running in production mode."""
    return config_manager.is_production()

def get_cors_origins() -> list:
    """Get CORS origins."""
    return config_manager.get_cors_origins()

def get_log_level() -> str:
    """Get logging level."""
    return config_manager.get_log_level()

# Configuration validation
def validate_config() -> bool:
    """Validate the current configuration."""
    config = get_config()
    errors = []
    
    # Validate required fields
    if not config.database.url:
        errors.append("Database URL is required")
    
    if not config.security.secret_key or config.security.secret_key == "dev-secret-key-change-in-production":
        if config.environment.lower() == "production":
            errors.append("Secret key must be set in production")
    
    if not config.security.access_code or config.security.access_code == "dev-access-code":
        if config.environment.lower() == "production":
            errors.append("Access code must be set in production")
    
    # Validate numeric fields
    if config.database.pool_size <= 0:
        errors.append("Database pool size must be positive")
    
    if config.cache.default_ttl <= 0:
        errors.append("Cache TTL must be positive")
    
    if errors:
        for error in errors:
            logger.error(f"Configuration validation error: {error}")
        return False
    
    logger.info("Configuration validation passed")
    return True

# Initialize configuration validation
if not validate_config():
    logger.warning("Configuration validation failed - some features may not work correctly")
