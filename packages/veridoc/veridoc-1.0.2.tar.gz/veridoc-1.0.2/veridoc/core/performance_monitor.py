"""
Performance Monitoring for VeriDoc
Memory usage, response times, and system metrics
"""

import time
import psutil
import logging
import asyncio
import functools
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""
    timestamp: float
    memory_usage_mb: float
    cpu_percent: float
    active_connections: int
    request_count: int
    average_response_time: float
    cache_hit_ratio: float
    index_size: int


@dataclass
class RequestMetrics:
    """Individual request metrics."""
    timestamp: float
    endpoint: str
    method: str
    response_time: float
    status_code: int
    memory_before: float
    memory_after: float


class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.start_time = time.time()
        self.request_history: deque = deque(maxlen=history_size)
        self.metrics_history: deque = deque(maxlen=100)  # Keep 100 snapshots
        self.active_connections = 0
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.lock = Lock()
        
        # Process reference for memory monitoring
        self.process = psutil.Process()
        
        # Background monitoring will be started when event loop is available
        self.monitoring_task = None
    
    async def start_monitoring(self):
        """Start background performance monitoring."""
        if self.monitoring_task is not None:
            return  # Already started
            
        async def monitor_loop():
            while True:
                try:
                    await asyncio.sleep(30)  # Collect metrics every 30 seconds
                    self._collect_metrics()
                except Exception as e:
                    logger.error(f"Performance monitoring error: {e}")
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(monitor_loop())
    
    def _collect_metrics(self):
        """Collect current performance metrics."""
        try:
            # Memory usage
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # CPU usage
            cpu_percent = self.process.cpu_percent()
            
            # Calculate average response time from recent requests
            with self.lock:
                recent_requests = list(self.request_history)
                total_requests = self.total_requests
                cache_hits = self.cache_hits
                cache_misses = self.cache_misses
            
            if recent_requests:
                avg_response_time = sum(req.response_time for req in recent_requests) / len(recent_requests)
            else:
                avg_response_time = 0.0
            
            # Cache hit ratio
            total_cache_requests = cache_hits + cache_misses
            cache_hit_ratio = cache_hits / max(total_cache_requests, 1)
            
            # Create metrics snapshot
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                memory_usage_mb=memory_mb,
                cpu_percent=cpu_percent,
                active_connections=self.active_connections,
                request_count=total_requests,
                average_response_time=avg_response_time,
                cache_hit_ratio=cache_hit_ratio,
                index_size=0  # Will be updated by search engine
            )
            
            # Add to history
            self.metrics_history.append(metrics)
            
            # Log warning if memory usage is high
            if memory_mb > 100:  # 100MB threshold
                logger.warning(f"High memory usage: {memory_mb:.1f}MB")
            
            # Log warning if response time is slow
            if avg_response_time > 1.0:  # 1 second threshold
                logger.warning(f"Slow response time: {avg_response_time:.2f}s")
                
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
    
    def record_request(self, 
                      endpoint: str,
                      method: str,
                      response_time: float,
                      status_code: int,
                      memory_before: Optional[float] = None,
                      memory_after: Optional[float] = None):
        """Record individual request metrics."""
        
        if memory_before is None:
            memory_before = self.get_memory_usage()
        if memory_after is None:
            memory_after = self.get_memory_usage()
        
        request = RequestMetrics(
            timestamp=time.time(),
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            memory_before=memory_before,
            memory_after=memory_after
        )
        
        with self.lock:
            self.request_history.append(request)
            self.total_requests += 1
    
    def record_cache_hit(self):
        """Record cache hit."""
        with self.lock:
            self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        with self.lock:
            self.cache_misses += 1
    
    def connection_opened(self):
        """Record new connection."""
        self.active_connections += 1
    
    def connection_closed(self):
        """Record connection closure."""
        self.active_connections = max(0, self.active_connections - 1)
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def get_uptime(self) -> float:
        """Get uptime in seconds."""
        return time.time() - self.start_time
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        memory_mb = self.get_memory_usage()
        uptime = self.get_uptime()
        
        # Calculate average response time from recent requests
        with self.lock:
            recent_requests = list(self.request_history)[-100:]  # Last 100 requests
            total_requests = self.total_requests
            cache_hits = self.cache_hits
            cache_misses = self.cache_misses
        
        if recent_requests:
            avg_response_time = sum(req.response_time for req in recent_requests) / len(recent_requests)
            min_response_time = min(req.response_time for req in recent_requests)
            max_response_time = max(req.response_time for req in recent_requests)
        else:
            avg_response_time = min_response_time = max_response_time = 0.0
        
        # Cache statistics
        total_cache_requests = cache_hits + cache_misses
        cache_hit_ratio = cache_hits / max(total_cache_requests, 1)
        
        # CPU usage
        try:
            cpu_percent = self.process.cpu_percent()
        except Exception:
            cpu_percent = 0.0
        
        return {
            "memory_usage_mb": round(memory_mb, 2),
            "uptime_seconds": round(uptime, 1),
            "cpu_percent": round(cpu_percent, 1),
            "active_connections": self.active_connections,
            "total_requests": total_requests,
            "requests_per_second": round(total_requests / max(uptime, 1), 2),
            "response_time": {
                "average": round(avg_response_time, 3),
                "min": round(min_response_time, 3),
                "max": round(max_response_time, 3)
            },
            "cache": {
                "hit_ratio": round(cache_hit_ratio, 3),
                "hits": cache_hits,
                "misses": cache_misses,
                "total": total_cache_requests
            }
        }
    
    def get_performance_summary(self, minutes: int = 10) -> Dict[str, Any]:
        """Get performance summary for last N minutes."""
        cutoff_time = time.time() - (minutes * 60)
        
        # Filter recent requests
        with self.lock:
            recent_requests = [req for req in self.request_history 
                             if req.timestamp >= cutoff_time]
        
        if not recent_requests:
            return {
                "period_minutes": minutes,
                "request_count": 0,
                "average_response_time": 0.0,
                "error_rate": 0.0,
                "slowest_endpoints": []
            }
        
        # Calculate statistics
        total_requests = len(recent_requests)
        error_requests = sum(1 for req in recent_requests if req.status_code >= 400)
        error_rate = error_requests / total_requests
        
        avg_response_time = sum(req.response_time for req in recent_requests) / total_requests
        
        # Find slowest endpoints
        endpoint_times = {}
        for req in recent_requests:
            if req.endpoint not in endpoint_times:
                endpoint_times[req.endpoint] = []
            endpoint_times[req.endpoint].append(req.response_time)
        
        slowest_endpoints = []
        for endpoint, times in endpoint_times.items():
            avg_time = sum(times) / len(times)
            slowest_endpoints.append({
                "endpoint": endpoint,
                "average_time": round(avg_time, 3),
                "request_count": len(times)
            })
        
        slowest_endpoints.sort(key=lambda x: x["average_time"], reverse=True)
        
        return {
            "period_minutes": minutes,
            "request_count": total_requests,
            "average_response_time": round(avg_response_time, 3),
            "error_rate": round(error_rate, 3),
            "slowest_endpoints": slowest_endpoints[:5]  # Top 5
        }
    
    def get_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get historical metrics for charts."""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_metrics = [
            asdict(metrics) for metrics in self.metrics_history
            if metrics.timestamp >= cutoff_time
        ]
        
        return recent_metrics
    
    def check_health(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        memory_mb = self.get_memory_usage()
        uptime = self.get_uptime()
        
        # Health status
        health_status = "healthy"
        issues = []
        
        # Check memory usage
        if memory_mb > 200:  # 200MB threshold
            health_status = "degraded"
            issues.append(f"High memory usage: {memory_mb:.1f}MB")
        
        # Check recent response times
        with self.lock:
            recent_requests = list(self.request_history)[-50:]  # Last 50 requests
        
        if recent_requests:
            avg_response_time = sum(req.response_time for req in recent_requests) / len(recent_requests)
            if avg_response_time > 2.0:  # 2 second threshold
                health_status = "degraded"
                issues.append(f"Slow response time: {avg_response_time:.2f}s")
        
        # Check error rate
        if recent_requests:
            error_count = sum(1 for req in recent_requests if req.status_code >= 500)
            error_rate = error_count / len(recent_requests)
            if error_rate > 0.1:  # 10% error rate
                health_status = "unhealthy"
                issues.append(f"High error rate: {error_rate:.1%}")
        
        return {
            "status": health_status,
            "uptime_seconds": round(uptime, 1),
            "memory_usage_mb": round(memory_mb, 2),
            "issues": issues
        }
    
    def reset_statistics(self):
        """Reset all statistics."""
        with self.lock:
            self.request_history.clear()
            self.total_requests = 0
            self.cache_hits = 0
            self.cache_misses = 0
        
        self.metrics_history.clear()
        self.active_connections = 0
        logger.info("Performance statistics reset")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def performance_tracking(func):
    """Decorator for tracking function performance."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        memory_before = performance_monitor.get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            status_code = 200
        except Exception as e:
            status_code = 500
            raise
        finally:
            end_time = time.time()
            memory_after = performance_monitor.get_memory_usage()
            response_time = end_time - start_time
            
            performance_monitor.record_request(
                endpoint=func.__name__,
                method="SYNC",
                response_time=response_time,
                status_code=status_code,
                memory_before=memory_before,
                memory_after=memory_after
            )
        
        return result
    
    return wrapper


def async_performance_tracking(func):
    """Decorator for tracking async function performance."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        memory_before = performance_monitor.get_memory_usage()
        
        try:
            result = await func(*args, **kwargs)
            status_code = 200
        except Exception as e:
            status_code = 500
            raise
        finally:
            end_time = time.time()
            memory_after = performance_monitor.get_memory_usage()
            response_time = end_time - start_time
            
            performance_monitor.record_request(
                endpoint=func.__name__,
                method="ASYNC",
                response_time=response_time,
                status_code=status_code,
                memory_before=memory_before,
                memory_after=memory_after
            )
        
        return result
    
    return wrapper