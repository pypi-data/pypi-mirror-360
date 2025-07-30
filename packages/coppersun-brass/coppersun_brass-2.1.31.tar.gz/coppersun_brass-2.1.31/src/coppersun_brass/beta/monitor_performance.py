#!/usr/bin/env python3
"""
Beta Performance Monitoring for Copper Alloy Brass v1.0
Tracks and reports on performance metrics during beta testing.
"""

import asyncio
import time
import psutil
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import httpx
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors Copper Alloy Brass performance in beta environment."""
    
    def __init__(self, 
                 api_url: str = "http://localhost:8001",
                 db_path: Path = Path("beta_metrics.db")):
        self.api_url = api_url
        self.db_path = db_path
        self._init_db()
        self._init_metrics()
        
    def _init_db(self):
        """Initialize metrics database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                endpoint TEXT,
                value REAL NOT NULL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                service TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time_ms REAL,
                error_message TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
    def _init_metrics(self):
        """Initialize Prometheus metrics."""
        self.request_count = Counter(
            'brass_requests_total',
            'Total API requests',
            ['endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'brass_request_duration_seconds',
            'Request duration in seconds',
            ['endpoint']
        )
        
        self.active_agents = Gauge(
            'brass_active_agents',
            'Number of active agents'
        )
        
        self.memory_usage = Gauge(
            'brass_memory_usage_mb',
            'Memory usage in MB'
        )
        
        self.cache_hit_rate = Gauge(
            'brass_cache_hit_rate',
            'Cache hit rate percentage'
        )
        
    async def monitor_endpoint(self, endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """Monitor a specific endpoint."""
        start_time = time.time()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=f"{self.api_url}{endpoint}",
                    timeout=30.0
                )
                
                duration = time.time() - start_time
                
                # Record metrics
                self.request_count.labels(
                    endpoint=endpoint,
                    status=response.status_code
                ).inc()
                
                self.request_duration.labels(endpoint=endpoint).observe(duration)
                
                # Store in database
                self._store_metric(
                    metric_type="api_response_time",
                    endpoint=endpoint,
                    value=duration * 1000,  # Convert to ms
                    metadata={
                        "status_code": response.status_code,
                        "method": method
                    }
                )
                
                return {
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "duration_ms": duration * 1000,
                    "success": response.status_code < 400
                }
                
            except Exception as e:
                self.request_count.labels(
                    endpoint=endpoint,
                    status="error"
                ).inc()
                
                logger.error(f"Error monitoring {endpoint}: {e}")
                
                return {
                    "endpoint": endpoint,
                    "status": "error",
                    "error": str(e),
                    "success": False
                }
                
    async def run_performance_test(self) -> Dict[str, Any]:
        """Run a comprehensive performance test."""
        logger.info("Starting performance test...")
        
        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {},
            "system_metrics": {},
            "analysis_performance": {}
        }
        
        # Test key endpoints
        endpoints = [
            "/health",
            "/api/v1/analyze",
            "/api/v1/observations",
            "/api/v1/recommendations",
            "/metrics"
        ]
        
        for endpoint in endpoints:
            result = await self.monitor_endpoint(endpoint)
            test_results["endpoints"][endpoint] = result
            
        # System metrics
        test_results["system_metrics"] = self._get_system_metrics()
        
        # Test analysis performance
        test_results["analysis_performance"] = await self._test_analysis_performance()
        
        # Store summary
        self._store_test_summary(test_results)
        
        return test_results
        
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        process = psutil.Process()
        
        metrics = {
            "cpu_percent": process.cpu_percent(interval=1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "open_files": len(process.open_files()),
            "threads": process.num_threads(),
            "connections": len(process.connections())
        }
        
        # Update Prometheus metrics
        self.memory_usage.set(metrics["memory_mb"])
        
        # Store in database
        for metric_name, value in metrics.items():
            self._store_metric(
                metric_type=f"system_{metric_name}",
                value=value
            )
            
        return metrics
        
    async def _test_analysis_performance(self) -> Dict[str, Any]:
        """Test analysis performance with different project sizes."""
        results = {}
        
        # Test scenarios
        scenarios = [
            {"name": "small", "files": 10},
            {"name": "medium", "files": 100},
            {"name": "large", "files": 1000}
        ]
        
        for scenario in scenarios:
            start_time = time.time()
            
            # Simulate analysis request
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{self.api_url}/api/v1/analyze",
                        json={
                            "project_size": scenario["files"],
                            "test_scenario": scenario["name"]
                        },
                        timeout=120.0
                    )
                    
                    duration = time.time() - start_time
                    
                    results[scenario["name"]] = {
                        "files": scenario["files"],
                        "duration_seconds": duration,
                        "files_per_second": scenario["files"] / duration,
                        "success": response.status_code == 200
                    }
                    
                except Exception as e:
                    results[scenario["name"]] = {
                        "files": scenario["files"],
                        "error": str(e),
                        "success": False
                    }
                    
        return results
        
    def _store_metric(self, 
                     metric_type: str, 
                     value: float,
                     endpoint: Optional[str] = None,
                     metadata: Optional[Dict] = None):
        """Store metric in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO performance_metrics (metric_type, endpoint, value, metadata)
            VALUES (?, ?, ?, ?)
        """, (
            metric_type,
            endpoint,
            value,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
        
    def _store_test_summary(self, results: Dict[str, Any]):
        """Store test summary for reporting."""
        summary_path = Path("beta_performance_summary.json")
        
        # Load existing summaries
        if summary_path.exists():
            with open(summary_path) as f:
                summaries = json.load(f)
        else:
            summaries = []
            
        summaries.append(results)
        
        # Keep last 100 test results
        summaries = summaries[-100:]
        
        with open(summary_path, 'w') as f:
            json.dump(summaries, f, indent=2)
            
    async def continuous_monitoring(self, interval: int = 60):
        """Run continuous monitoring."""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                # Run health checks
                await self._health_check_all()
                
                # Get system metrics
                self._get_system_metrics()
                
                # Test random endpoint
                import random
                endpoint = random.choice([
                    "/api/v1/observations",
                    "/api/v1/recommendations",
                    "/metrics"
                ])
                await self.monitor_endpoint(endpoint)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                
            await asyncio.sleep(interval)
            
    async def _health_check_all(self):
        """Check health of all services."""
        services = [
            ("api", f"{self.api_url}/health"),
            ("prometheus", "http://localhost:9090/-/healthy"),
            ("grafana", "http://localhost:3000/api/health")
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for service_name, url in services:
            start_time = time.time()
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=5.0)
                    response_time = (time.time() - start_time) * 1000
                    
                    status = "healthy" if response.status_code == 200 else "unhealthy"
                    
                    cursor.execute("""
                        INSERT INTO health_checks (service, status, response_time_ms)
                        VALUES (?, ?, ?)
                    """, (service_name, status, response_time))
                    
            except Exception as e:
                cursor.execute("""
                    INSERT INTO health_checks (service, status, error_message)
                    VALUES (?, ?, ?)
                """, (service_name, "error", str(e)))
                
        conn.commit()
        conn.close()
        
    def generate_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate performance report for the last N hours."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        report = {
            "period": f"Last {hours} hours",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {},
            "endpoints": {},
            "system": {},
            "health": {}
        }
        
        # API performance summary
        cursor.execute("""
            SELECT 
                endpoint,
                COUNT(*) as request_count,
                AVG(value) as avg_response_time_ms,
                MIN(value) as min_response_time_ms,
                MAX(value) as max_response_time_ms,
                CAST(SUM(CASE WHEN value < 1000 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100 as under_1s_percent
            FROM performance_metrics
            WHERE metric_type = 'api_response_time'
                AND timestamp > ?
            GROUP BY endpoint
        """, (since,))
        
        for row in cursor.fetchall():
            report["endpoints"][row["endpoint"]] = dict(row)
            
        # System metrics summary
        cursor.execute("""
            SELECT 
                metric_type,
                AVG(value) as avg_value,
                MAX(value) as max_value
            FROM performance_metrics
            WHERE metric_type LIKE 'system_%'
                AND timestamp > ?
            GROUP BY metric_type
        """, (since,))
        
        for row in cursor.fetchall():
            metric_name = row["metric_type"].replace("system_", "")
            report["system"][metric_name] = {
                "average": row["avg_value"],
                "peak": row["max_value"]
            }
            
        # Health check summary
        cursor.execute("""
            SELECT 
                service,
                COUNT(*) as total_checks,
                SUM(CASE WHEN status = 'healthy' THEN 1 ELSE 0 END) as healthy_checks,
                AVG(response_time_ms) as avg_response_time
            FROM health_checks
            WHERE timestamp > ?
            GROUP BY service
        """, (since,))
        
        for row in cursor.fetchall():
            uptime_percent = (row["healthy_checks"] / row["total_checks"] * 100) if row["total_checks"] > 0 else 0
            report["health"][row["service"]] = {
                "uptime_percent": uptime_percent,
                "avg_response_time_ms": row["avg_response_time"]
            }
            
        conn.close()
        return report


async def main():
    """Main monitoring function."""
    monitor = PerformanceMonitor()
    
    # Run initial performance test
    print("Running initial performance test...")
    results = await monitor.run_performance_test()
    print(json.dumps(results, indent=2))
    
    # Generate report
    print("\nGenerating performance report...")
    report = monitor.generate_report(hours=1)
    print(json.dumps(report, indent=2))
    
    # Start continuous monitoring
    print("\nStarting continuous monitoring...")
    await monitor.continuous_monitoring(interval=60)


if __name__ == "__main__":
    asyncio.run(main())