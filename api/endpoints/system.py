"""
System Management API for Sprint 3 Architecture Improvements
Provides endpoints for monitoring and managing system components.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from core.config import get_config, config_manager
from core.connection_pool import get_connection_stats, health_check as db_health_check
from core.background_jobs import get_job_stats, get_default_queue
from core.event_system import event_handler, EventTypes
from core.cache import cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/health")
async def system_health() -> Dict[str, Any]:
    """Get overall system health status."""
    try:
        # Check database health
        db_health = await db_health_check()
        
        # Check cache health
        cache_health = {
            "status": "healthy" if cache else "error",
            "cache_size": cache.size() if cache else 0,
            "default_ttl": cache.default_ttl if cache else 0
        }
        
        # Check job queue health
        job_stats = get_job_stats()
        job_health = {
            "status": "healthy" if job_stats else "error",
            "queues": len(job_stats),
            "stats": job_stats
        }
        
        # Check event system health
        event_health = {
            "status": "healthy",
            "event_types": len(event_handler.get_all_event_types()),
            "total_events": len(event_handler.get_event_history())
        }
        
        # Overall health status
        overall_status = "healthy"
        if (db_health["status"] == "error" or 
            cache_health["status"] == "error" or 
            job_health["status"] == "error"):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": db_health,
                "cache": cache_health,
                "job_queues": job_health,
                "event_system": event_health
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@router.get("/stats")
async def system_stats() -> Dict[str, Any]:
    """Get detailed system statistics."""
    try:
        config = get_config()
        
        return {
            "environment": config.environment,
            "debug": config.debug,
            "database": {
                "url": config.database.url.split("://")[0] + "://***",  # Hide credentials
                "pool_size": config.database.pool_size,
                "echo": config.database.echo
            },
            "cache": {
                "enabled": config.cache.enabled,
                "default_ttl": config.cache.default_ttl,
                "max_size": config.cache.max_size
            },
            "websocket": {
                "enabled": config.websocket.enabled,
                "max_connections": config.websocket.max_connections
            },
            "performance": {
                "profiling_enabled": config.performance.enable_profiling,
                "slow_query_threshold": config.performance.slow_query_threshold
            },
            "connection_pool": get_connection_stats(),
            "job_queues": get_job_stats(),
            "event_system": {
                "event_types": event_handler.get_all_event_types(),
                "recent_events": len(event_handler.get_event_history(limit=100))
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {e}")

@router.get("/config")
async def get_system_config() -> Dict[str, Any]:
    """Get current system configuration."""
    try:
        config = get_config()
        
        # Return safe configuration (hide sensitive data)
        return {
            "environment": config.environment,
            "debug": config.debug,
            "host": config.host,
            "port": config.port,
            "database": {
                "echo": config.database.echo,
                "pool_size": config.database.pool_size,
                "max_overflow": config.database.max_overflow,
                "pool_timeout": config.database.pool_timeout,
                "pool_recycle": config.database.pool_recycle
            },
            "cache": {
                "enabled": config.cache.enabled,
                "default_ttl": config.cache.default_ttl,
                "max_size": config.cache.max_size,
                "cleanup_interval": config.cache.cleanup_interval
            },
            "websocket": {
                "enabled": config.websocket.enabled,
                "max_connections": config.websocket.max_connections,
                "heartbeat_interval": config.websocket.heartbeat_interval,
                "connection_timeout": config.websocket.connection_timeout
            },
            "security": {
                "cors_origins": config.security.cors_origins,
                "rate_limit_enabled": config.security.rate_limit_enabled,
                "rate_limit_requests": config.security.rate_limit_requests,
                "rate_limit_window": config.security.rate_limit_window
            },
            "logging": {
                "level": config.logging.level,
                "file_enabled": config.logging.file_enabled,
                "max_file_size": config.logging.max_file_size,
                "backup_count": config.logging.backup_count
            },
            "performance": {
                "enable_profiling": config.performance.enable_profiling,
                "slow_query_threshold": config.performance.slow_query_threshold,
                "max_request_size": config.performance.max_request_size,
                "request_timeout": config.performance.request_timeout
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system config: {e}")

@router.post("/config")
async def update_system_config(config_updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update system configuration (development only)."""
    try:
        config = get_config()
        
        # Only allow config updates in development
        if config.environment.lower() != "development":
            raise HTTPException(status_code=403, detail="Configuration updates only allowed in development")
        
        # Update configuration
        config_manager.update_config(config_updates)
        
        # Emit configuration change event
        await event_handler.emit(
            EventTypes.SYSTEM_STARTUP,  # We'll add a CONFIG_UPDATED event type
            {
                "updated_fields": list(config_updates.keys()),
                "timestamp": event_handler.get_event_history(limit=1)[0].timestamp.isoformat() if event_handler.get_event_history(limit=1) else None
            },
            source="config_api"
        )
        
        return {
            "message": "Configuration updated successfully",
            "updated_fields": list(config_updates.keys())
        }
        
    except Exception as e:
        logger.error(f"Failed to update system config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update system config: {e}")

@router.get("/events")
async def get_event_history(limit: int = 50, event_type: str = None) -> Dict[str, Any]:
    """Get recent event history."""
    try:
        events = event_handler.get_event_history(event_type, limit)
        
        return {
            "events": [
                {
                    "type": event.type,
                    "source": event.source,
                    "timestamp": event.timestamp.isoformat(),
                    "target": event.target,
                    "data": event.data
                }
                for event in events
            ],
            "total_events": len(events),
            "event_type": event_type,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to get event history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get event history: {e}")

@router.get("/jobs")
async def get_job_queue_status() -> Dict[str, Any]:
    """Get job queue status and statistics."""
    try:
        return {
            "queues": get_job_stats(),
            "default_queue": get_default_queue().get_queue_stats()
        }
        
    except Exception as e:
        logger.error(f"Failed to get job queue status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job queue status: {e}")

@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, queue_name: str = "default") -> Dict[str, Any]:
    """Cancel a background job."""
    try:
        from core.background_jobs import cancel_job as cancel_job_func
        
        success = cancel_job_func(job_id, queue_name)
        
        if success:
            return {"message": f"Job {job_id} cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found or cannot be cancelled")
            
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {e}")

@router.get("/cache")
async def get_cache_info() -> Dict[str, Any]:
    """Get cache information and statistics."""
    try:
        if not cache:
            return {"status": "disabled", "message": "Cache is not enabled"}
        
        return {
            "status": "enabled",
            "cache_size": cache.size(),
            "default_ttl": cache.default_ttl
        }
        
    except Exception as e:
        logger.error(f"Failed to get cache info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache info: {e}")

@router.post("/cache/clear")
async def clear_cache() -> Dict[str, Any]:
    """Clear the cache (development only)."""
    try:
        config = get_config()
        
        # Only allow cache clearing in development
        if config.environment.lower() != "development":
            raise HTTPException(status_code=403, detail="Cache clearing only allowed in development")
        
        if cache:
            cache.clear()
            
            # Emit cache cleared event
            await event_handler.emit(
                EventTypes.SYSTEM_STARTUP,  # We'll add a CACHE_CLEARED event type
                {"cleared_at": event_handler.get_event_history(limit=1)[0].timestamp.isoformat() if event_handler.get_event_history(limit=1) else None},
                source="cache_api"
            )
            
            return {"message": "Cache cleared successfully"}
        else:
            return {"message": "Cache is not enabled"}
            
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {e}")

@router.get("/database")
async def get_database_info() -> Dict[str, Any]:
    """Get database connection information."""
    try:
        return {
            "connection_stats": get_connection_stats(),
            "health": await db_health_check()
        }
        
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get database info: {e}")
