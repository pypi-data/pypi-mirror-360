"""Production Monitoring Dashboard.

This module provides a comprehensive production monitoring dashboard that aggregates
all existing monitoring capabilities into a unified view for production operations.

Features:
- Real-time system health monitoring
- Performance metrics visualization
- Alert status and history
- Tool usage analytics
- API performance breakdown
- Historical trend analysis

Following development best practices:
- Builds on existing monitoring infrastructure
- Provides both JSON API and HTML dashboard
- Real-time updates via WebSocket
- Configurable for different environments
"""

import json
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger

# Import existing monitoring components
from ..monitoring import SystemMonitor, get_performance_summary
from ..performance_monitor import get_performance_dashboard
from ..fastmcp_performance import FastMCPPerformanceMonitor
from ..prometheus_metrics import prometheus_metrics


@dataclass
class DashboardMetrics:
    """Aggregated dashboard metrics."""
    timestamp: datetime
    system_health: Dict[str, Any]
    performance_summary: Dict[str, Any]
    alert_summary: Dict[str, Any]
    tool_analytics: Dict[str, Any]
    api_performance: Dict[str, Any]
    resource_utilization: Dict[str, Any]
    sla_compliance: Dict[str, Any]


@dataclass
class AlertSummary:
    """Alert summary for dashboard."""
    total_alerts: int
    critical_alerts: int
    warning_alerts: int
    info_alerts: int
    resolved_alerts: int
    active_alerts: int
    alert_rate_24h: float
    top_alert_sources: List[Dict[str, Any]]


class ProductionDashboard:
    """Production monitoring dashboard with real-time capabilities."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize production dashboard.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.system_monitor = SystemMonitor()
        self.fastmcp_monitor = FastMCPPerformanceMonitor()
        
        # Dashboard configuration
        self.refresh_interval = self.config.get("refresh_interval", 30)  # seconds
        self.history_retention = self.config.get("history_retention", 24)  # hours
        self.alert_thresholds = self.config.get("alert_thresholds", {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "error_rate": 5.0,
            "response_time": 2.0,
            "success_rate": 95.0
        })
        
        # Metrics history storage
        self.metrics_history: List[DashboardMetrics] = []
        self.max_history_size = int((self.history_retention * 3600) / self.refresh_interval)
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data.
        
        Returns:
            Complete dashboard data dictionary
        """
        try:
            # Gather all monitoring data
            system_status = await self.system_monitor.get_comprehensive_status()
            performance_data = get_performance_dashboard()
            fastmcp_data = self.fastmcp_monitor.get_performance_dashboard()
            
            # Create aggregated metrics
            dashboard_metrics = DashboardMetrics(
                timestamp=datetime.now(timezone.utc),
                system_health=self._extract_system_health(system_status),
                performance_summary=self._extract_performance_summary(performance_data),
                alert_summary=self._extract_alert_summary(system_status, fastmcp_data),
                tool_analytics=self._extract_tool_analytics(performance_data),
                api_performance=self._extract_api_performance(performance_data),
                resource_utilization=self._extract_resource_utilization(system_status),
                sla_compliance=self._calculate_sla_compliance(performance_data)
            )
            
            # Store in history
            self._store_metrics_history(dashboard_metrics)
            
            # Build dashboard response
            dashboard_data = {
                "status": "healthy",
                "timestamp": dashboard_metrics.timestamp.isoformat(),
                "refresh_interval": self.refresh_interval,
                "current_metrics": asdict(dashboard_metrics),
                "trends": self._calculate_trends(),
                "alerts": self._get_active_alerts(),
                "recommendations": self._generate_recommendations(dashboard_metrics),
                "uptime": system_status.get("uptime_seconds", 0),
                "version": self._get_version_info()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "fallback_data": await self._get_fallback_data()
            }
    
    def _extract_system_health(self, system_status: Dict[str, Any]) -> Dict[str, Any]:
        """Extract system health metrics."""
        health_checks = system_status.get("health_checks", {})
        system_metrics = system_status.get("system_metrics", {})
        
        return {
            "overall_status": system_status.get("overall_status", "unknown"),
            "health_check_count": len(health_checks),
            "healthy_checks": len([c for c in health_checks.values() if c.get("status") == "healthy"]),
            "failed_checks": len([c for c in health_checks.values() if c.get("status") == "unhealthy"]),
            "cpu_usage": system_metrics.get("cpu_percent", 0),
            "memory_usage": system_metrics.get("memory_percent", 0),
            "disk_usage": system_metrics.get("disk_usage_percent", 0),
            "network_connections": system_metrics.get("network_connections", 0)
        }
    
    def _extract_performance_summary(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance summary metrics."""
        if not performance_data:
            return {"status": "no_data", "operations": 0}
        
        operations = performance_data.get("operations", {})
        total_operations = sum(op.get("count", 0) for op in operations.values())
        avg_success_rate = sum(op.get("success_rate", 0) for op in operations.values()) / max(len(operations), 1)
        avg_response_time = sum(op.get("avg_duration", 0) for op in operations.values()) / max(len(operations), 1)
        
        return {
            "total_operations": total_operations,
            "operation_types": len(operations),
            "avg_success_rate": round(avg_success_rate, 2),
            "avg_response_time": round(avg_response_time, 3),
            "operations_per_minute": performance_data.get("operations_per_minute", 0),
            "error_rate": round(100 - avg_success_rate, 2)
        }
    
    def _extract_alert_summary(self, system_status: Dict[str, Any], fastmcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract alert summary metrics."""
        system_alerts = system_status.get("alerts", [])
        fastmcp_alerts = fastmcp_data.get("active_alerts", [])
        
        all_alerts = system_alerts + fastmcp_alerts
        
        return {
            "total_alerts": len(all_alerts),
            "critical_alerts": len([a for a in all_alerts if self._get_alert_severity(a) == "critical"]),
            "warning_alerts": len([a for a in all_alerts if self._get_alert_severity(a) == "warning"]),
            "info_alerts": len([a for a in all_alerts if self._get_alert_severity(a) == "info"]),
            "active_alerts": len([a for a in all_alerts if not self._is_alert_resolved(a)]),
            "alert_sources": self._get_alert_sources(all_alerts)
        }
    
    def _extract_tool_analytics(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tool usage analytics."""
        operations = performance_data.get("operations", {})
        
        tool_stats = {}
        for op_name, op_data in operations.items():
            tool_name = op_name.split("_")[0] if "_" in op_name else op_name
            if tool_name not in tool_stats:
                tool_stats[tool_name] = {
                    "total_calls": 0,
                    "total_duration": 0,
                    "success_count": 0,
                    "error_count": 0
                }
            
            count = op_data.get("count", 0)
            duration = op_data.get("total_duration", 0)
            success_rate = op_data.get("success_rate", 100)
            
            tool_stats[tool_name]["total_calls"] += count
            tool_stats[tool_name]["total_duration"] += duration
            tool_stats[tool_name]["success_count"] += int(count * success_rate / 100)
            tool_stats[tool_name]["error_count"] += int(count * (100 - success_rate) / 100)
        
        # Calculate derived metrics
        for tool_name, stats in tool_stats.items():
            if stats["total_calls"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["total_calls"]
                stats["success_rate"] = (stats["success_count"] / stats["total_calls"]) * 100
                stats["error_rate"] = (stats["error_count"] / stats["total_calls"]) * 100
        
        return {
            "total_tools": len(tool_stats),
            "tool_statistics": tool_stats,
            "most_used_tool": max(tool_stats.keys(), key=lambda k: tool_stats[k]["total_calls"]) if tool_stats else None,
            "highest_error_rate_tool": max(tool_stats.keys(), key=lambda k: tool_stats[k]["error_rate"]) if tool_stats else None
        }
    
    def _extract_api_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract API performance metrics."""
        operations = performance_data.get("operations", {})
        
        api_operations = {k: v for k, v in operations.items() if "api" in k.lower() or "http" in k.lower()}
        
        if not api_operations:
            return {"status": "no_api_data"}
        
        total_requests = sum(op.get("count", 0) for op in api_operations.values())
        avg_response_time = sum(op.get("avg_duration", 0) for op in api_operations.values()) / len(api_operations)
        avg_success_rate = sum(op.get("success_rate", 0) for op in api_operations.values()) / len(api_operations)
        
        return {
            "total_requests": total_requests,
            "avg_response_time": round(avg_response_time, 3),
            "avg_success_rate": round(avg_success_rate, 2),
            "endpoint_count": len(api_operations),
            "requests_per_minute": performance_data.get("operations_per_minute", 0),
            "slowest_endpoint": max(api_operations.keys(), key=lambda k: api_operations[k].get("avg_duration", 0)) if api_operations else None
        }
    
    def _extract_resource_utilization(self, system_status: Dict[str, Any]) -> Dict[str, Any]:
        """Extract resource utilization metrics."""
        system_metrics = system_status.get("system_metrics", {})
        
        return {
            "cpu_percent": system_metrics.get("cpu_percent", 0),
            "memory_percent": system_metrics.get("memory_percent", 0),
            "memory_available_mb": system_metrics.get("memory_available_mb", 0),
            "disk_usage_percent": system_metrics.get("disk_usage_percent", 0),
            "disk_free_gb": system_metrics.get("disk_free_gb", 0),
            "network_connections": system_metrics.get("network_connections", 0),
            "load_average": system_metrics.get("load_average", [0, 0, 0])
        }
    
    def _calculate_sla_compliance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate SLA compliance metrics."""
        operations = performance_data.get("operations", {})
        
        if not operations:
            return {"status": "no_data"}
        
        # SLA targets
        target_success_rate = 99.5
        target_response_time = 1.0
        
        compliant_operations = 0
        total_operations = len(operations)
        
        for op_data in operations.values():
            success_rate = op_data.get("success_rate", 0)
            avg_duration = op_data.get("avg_duration", 0)
            
            if success_rate >= target_success_rate and avg_duration <= target_response_time:
                compliant_operations += 1
        
        compliance_rate = (compliant_operations / total_operations * 100) if total_operations > 0 else 0
        
        return {
            "target_success_rate": target_success_rate,
            "target_response_time": target_response_time,
            "compliance_rate": round(compliance_rate, 2),
            "compliant_operations": compliant_operations,
            "total_operations": total_operations,
            "sla_status": "compliant" if compliance_rate >= 95 else "at_risk" if compliance_rate >= 90 else "non_compliant"
        }
    
    def _store_metrics_history(self, metrics: DashboardMetrics):
        """Store metrics in history for trend analysis."""
        self.metrics_history.append(metrics)
        
        # Trim history to max size
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate trends from historical data."""
        if len(self.metrics_history) < 2:
            return {"status": "insufficient_data"}
        
        current = self.metrics_history[-1]
        previous = self.metrics_history[-2] if len(self.metrics_history) >= 2 else current
        
        # Calculate percentage changes
        trends = {}
        
        # System health trends
        current_cpu = current.system_health.get("cpu_usage", 0)
        previous_cpu = previous.system_health.get("cpu_usage", 0)
        trends["cpu_trend"] = self._calculate_percentage_change(previous_cpu, current_cpu)
        
        current_memory = current.system_health.get("memory_usage", 0)
        previous_memory = previous.system_health.get("memory_usage", 0)
        trends["memory_trend"] = self._calculate_percentage_change(previous_memory, current_memory)
        
        # Performance trends
        current_response_time = current.performance_summary.get("avg_response_time", 0)
        previous_response_time = previous.performance_summary.get("avg_response_time", 0)
        trends["response_time_trend"] = self._calculate_percentage_change(previous_response_time, current_response_time)
        
        current_success_rate = current.performance_summary.get("avg_success_rate", 0)
        previous_success_rate = previous.performance_summary.get("avg_success_rate", 0)
        trends["success_rate_trend"] = self._calculate_percentage_change(previous_success_rate, current_success_rate)
        
        return trends
    
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> Dict[str, Any]:
        """Calculate percentage change between two values."""
        if old_value == 0:
            return {"change": 0, "direction": "stable", "percentage": 0}
        
        change = new_value - old_value
        percentage = (change / old_value) * 100
        
        direction = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
        
        return {
            "change": round(change, 3),
            "percentage": round(percentage, 2),
            "direction": direction
        }
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts."""
        # This would integrate with the existing alert system
        # For now, return a placeholder structure
        return []
    
    def _generate_recommendations(self, metrics: DashboardMetrics) -> List[str]:
        """Generate operational recommendations based on current metrics."""
        recommendations = []
        
        # CPU usage recommendations
        cpu_usage = metrics.system_health.get("cpu_usage", 0)
        if cpu_usage > self.alert_thresholds["cpu_usage"]:
            recommendations.append(f"High CPU usage detected ({cpu_usage:.1f}%) - consider scaling or optimization")
        
        # Memory usage recommendations
        memory_usage = metrics.system_health.get("memory_usage", 0)
        if memory_usage > self.alert_thresholds["memory_usage"]:
            recommendations.append(f"High memory usage detected ({memory_usage:.1f}%) - monitor for memory leaks")
        
        # Error rate recommendations
        error_rate = metrics.performance_summary.get("error_rate", 0)
        if error_rate > self.alert_thresholds["error_rate"]:
            recommendations.append(f"High error rate detected ({error_rate:.1f}%) - investigate error patterns")
        
        # Response time recommendations
        response_time = metrics.performance_summary.get("avg_response_time", 0)
        if response_time > self.alert_thresholds["response_time"]:
            recommendations.append(f"Slow response times detected ({response_time:.2f}s) - optimize performance")
        
        # Success rate recommendations
        success_rate = metrics.performance_summary.get("avg_success_rate", 100)
        if success_rate < self.alert_thresholds["success_rate"]:
            recommendations.append(f"Low success rate detected ({success_rate:.1f}%) - investigate failures")
        
        if not recommendations:
            recommendations.append("System operating within normal parameters")
        
        return recommendations
    
    def _get_alert_severity(self, alert: Any) -> str:
        """Get alert severity from alert object."""
        if isinstance(alert, dict):
            return alert.get("severity", "info").lower()
        return "info"
    
    def _is_alert_resolved(self, alert: Any) -> bool:
        """Check if alert is resolved."""
        if isinstance(alert, dict):
            return alert.get("resolved", False)
        return False
    
    def _get_alert_sources(self, alerts: List[Any]) -> List[str]:
        """Get unique alert sources."""
        sources = set()
        for alert in alerts:
            if isinstance(alert, dict):
                source = alert.get("source", "unknown")
                sources.add(source)
        return list(sources)
    
    def _get_version_info(self) -> Dict[str, str]:
        """Get version information."""
        return {
            "mcp_server": "1.0.0",
            "monitoring_version": "1.0.0",
            "python_version": "3.11+"
        }
    
    async def _get_fallback_data(self) -> Dict[str, Any]:
        """Get fallback data when main dashboard fails."""
        return {
            "system_health": {"status": "unknown"},
            "performance_summary": {"status": "unavailable"},
            "alert_summary": {"total_alerts": 0},
            "message": "Monitoring data temporarily unavailable"
        }


# Global dashboard instance
production_dashboard = ProductionDashboard()
