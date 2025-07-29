"""
Enterprise-grade observability and metrics for AA Kit

Provides comprehensive monitoring, metrics collection, distributed tracing,
and performance analytics for all AA Kit components and operations.
"""

import asyncio
import logging
import time
import threading
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
from collections import defaultdict, deque
import json
import uuid

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"           # Monotonically increasing
    GAUGE = "gauge"              # Current value
    HISTOGRAM = "histogram"       # Distribution of values
    TIMER = "timer"              # Duration measurements
    RATE = "rate"                # Rate of events


class LogLevel(Enum):
    """Log levels for structured logging."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class MetricPoint:
    """A single metric data point."""
    
    name: str
    value: Union[int, float]
    type: MetricType
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.type.value,
            'timestamp': self.timestamp,
            'tags': self.tags,
            'metadata': self.metadata
        }


@dataclass
class TraceSpan:
    """A distributed tracing span."""
    
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"
    
    @property
    def duration(self) -> Optional[float]:
        """Get span duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    def add_log(self, level: LogLevel, message: str, **kwargs):
        """Add log entry to span."""
        self.logs.append({
            'timestamp': time.time(),
            'level': level.value,
            'message': message,
            'fields': kwargs
        })
    
    def set_tag(self, key: str, value: str):
        """Set a tag on the span."""
        self.tags[key] = value
    
    def finish(self, status: str = "completed"):
        """Finish the span."""
        self.end_time = time.time()
        self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'span_id': self.span_id,
            'trace_id': self.trace_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'tags': self.tags,
            'logs': self.logs,
            'status': self.status
        }


class MetricCollector:
    """Thread-safe metric collector with aggregation."""
    
    def __init__(self, max_points: int = 10000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
        # Performance counters
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
    
    def record_metric(self, metric: MetricPoint):
        """Record a metric point."""
        with self._lock:
            metric_key = f"{metric.name}:{':'.join(f'{k}={v}' for k, v in sorted(metric.tags.items()))}"
            self.metrics[metric_key].append(metric)
            
            # Update typed collections for fast aggregation
            if metric.type == MetricType.COUNTER:
                self.counters[metric_key] += metric.value
            elif metric.type == MetricType.GAUGE:
                self.gauges[metric_key] = metric.value
            elif metric.type == MetricType.HISTOGRAM:
                self.histograms[metric_key].append(metric.value)
                # Keep only recent values
                if len(self.histograms[metric_key]) > 1000:
                    self.histograms[metric_key] = self.histograms[metric_key][-500:]
            elif metric.type == MetricType.TIMER:
                self.timers[metric_key].append(metric.value)
                if len(self.timers[metric_key]) > 1000:
                    self.timers[metric_key] = self.timers[metric_key][-500:]
    
    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get aggregated summary for a metric."""
        with self._lock:
            matching_keys = [k for k in self.metrics.keys() if k.startswith(f"{metric_name}:")]
            
            if not matching_keys:
                return {}
            
            summary = {
                'name': metric_name,
                'total_points': sum(len(self.metrics[k]) for k in matching_keys),
                'series_count': len(matching_keys),
                'counters': {},
                'gauges': {},
                'histograms': {},
                'timers': {}
            }
            
            # Aggregate by type
            for key in matching_keys:
                if key in self.counters:
                    summary['counters'][key] = self.counters[key]
                if key in self.gauges:
                    summary['gauges'][key] = self.gauges[key]
                if key in self.histograms and self.histograms[key]:
                    values = self.histograms[key]
                    summary['histograms'][key] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'mean': sum(values) / len(values),
                        'p50': self._percentile(values, 0.5),
                        'p95': self._percentile(values, 0.95),
                        'p99': self._percentile(values, 0.99)
                    }
                if key in self.timers and self.timers[key]:
                    values = self.timers[key]
                    summary['timers'][key] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'mean': sum(values) / len(values),
                        'p50': self._percentile(values, 0.5),
                        'p95': self._percentile(values, 0.95),
                        'p99': self._percentile(values, 0.99)
                    }
            
            return summary
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics summary."""
        with self._lock:
            metric_names = set(key.split(':')[0] for key in self.metrics.keys())
            return {
                name: self.get_metric_summary(name)
                for name in metric_names
            }


class DistributedTracer:
    """Distributed tracing system for request flow tracking."""
    
    def __init__(self, service_name: str = "omniagent"):
        self.service_name = service_name
        self.active_spans: Dict[str, TraceSpan] = {}
        self.completed_spans: deque = deque(maxlen=1000)
        self._context_spans: Dict[int, str] = {}  # Thread ID -> Span ID
        self._lock = threading.Lock()
    
    def start_span(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> TraceSpan:
        """Start a new tracing span."""
        if trace_id is None:
            # Try to get from current context
            current_span_id = self._get_current_span_id()
            if current_span_id and current_span_id in self.active_spans:
                trace_id = self.active_spans[current_span_id].trace_id
            else:
                trace_id = str(uuid.uuid4())
        
        if parent_span_id is None:
            parent_span_id = self._get_current_span_id()
        
        span = TraceSpan(
            span_id=str(uuid.uuid4()),
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time(),
            tags=tags or {}
        )
        
        span.set_tag('service.name', self.service_name)
        
        with self._lock:
            self.active_spans[span.span_id] = span
            self._set_current_span_id(span.span_id)
        
        return span
    
    def finish_span(self, span: TraceSpan, status: str = "completed"):
        """Finish a tracing span."""
        span.finish(status)
        
        with self._lock:
            if span.span_id in self.active_spans:
                del self.active_spans[span.span_id]
            self.completed_spans.append(span)
            
            # Clear from context if it's the current span
            if self._get_current_span_id() == span.span_id:
                self._clear_current_span_id()
    
    def _get_current_span_id(self) -> Optional[str]:
        """Get current span ID for this thread."""
        thread_id = threading.get_ident()
        return self._context_spans.get(thread_id)
    
    def _set_current_span_id(self, span_id: str):
        """Set current span ID for this thread."""
        thread_id = threading.get_ident()
        self._context_spans[thread_id] = span_id
    
    def _clear_current_span_id(self):
        """Clear current span ID for this thread."""
        thread_id = threading.get_ident()
        self._context_spans.pop(thread_id, None)
    
    @asynccontextmanager
    async def trace_operation(
        self,
        operation_name: str,
        tags: Optional[Dict[str, str]] = None
    ):
        """Context manager for tracing an operation."""
        span = self.start_span(operation_name, tags=tags)
        try:
            yield span
        except Exception as e:
            span.add_log(LogLevel.ERROR, f"Operation failed: {str(e)}")
            span.set_tag('error', 'true')
            self.finish_span(span, "error")
            raise
        else:
            self.finish_span(span, "completed")
    
    def get_trace_stats(self) -> Dict[str, Any]:
        """Get tracing statistics."""
        with self._lock:
            completed_count = len(self.completed_spans)
            active_count = len(self.active_spans)
            
            # Analyze completed spans
            if self.completed_spans:
                durations = [s.duration for s in self.completed_spans if s.duration]
                operations = defaultdict(int)
                errors = 0
                
                for span in self.completed_spans:
                    operations[span.operation_name] += 1
                    if span.status == 'error':
                        errors += 1
                
                avg_duration = sum(durations) / len(durations) if durations else 0
                
                return {
                    'completed_spans': completed_count,
                    'active_spans': active_count,
                    'error_rate': errors / completed_count * 100 if completed_count > 0 else 0,
                    'average_duration': avg_duration,
                    'operations': dict(operations),
                    'service_name': self.service_name
                }
            
            return {
                'completed_spans': 0,
                'active_spans': active_count,
                'error_rate': 0,
                'average_duration': 0,
                'operations': {},
                'service_name': self.service_name
            }


class PerformanceMonitor:
    """Real-time performance monitoring and alerting."""
    
    def __init__(self):
        self.start_time = time.time()
        self.measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def record_performance(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance measurement."""
        with self._lock:
            self.measurements[metric_name].append({
                'value': value,
                'timestamp': time.time(),
                'tags': tags or {}
            })
            
            # Check thresholds
            self._check_thresholds(metric_name, value)
    
    def set_threshold(
        self,
        metric_name: str,
        warning_threshold: float,
        critical_threshold: float
    ):
        """Set alert thresholds for a metric."""
        self.thresholds[metric_name] = {
            'warning': warning_threshold,
            'critical': critical_threshold
        }
    
    def _check_thresholds(self, metric_name: str, value: float):
        """Check if metric value exceeds thresholds."""
        if metric_name not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric_name]
        alert_level = None
        
        if value >= thresholds['critical']:
            alert_level = 'critical'
        elif value >= thresholds['warning']:
            alert_level = 'warning'
        
        if alert_level:
            alert = {
                'timestamp': time.time(),
                'metric': metric_name,
                'value': value,
                'level': alert_level,
                'threshold': thresholds[alert_level],
                'message': f"{metric_name} exceeded {alert_level} threshold: {value} >= {thresholds[alert_level]}"
            }
            self.alerts.append(alert)
            
            # Keep only recent alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-50:]
            
            logger.warning(f"Performance alert: {alert['message']}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance monitoring summary."""
        with self._lock:
            summary = {
                'uptime_seconds': time.time() - self.start_time,
                'monitored_metrics': len(self.measurements),
                'total_alerts': len(self.alerts),
                'recent_alerts': [a for a in self.alerts if time.time() - a['timestamp'] < 300],  # Last 5 minutes
                'metrics': {}
            }
            
            for metric_name, measurements in self.measurements.items():
                if measurements:
                    values = [m['value'] for m in measurements]
                    summary['metrics'][metric_name] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'mean': sum(values) / len(values),
                        'latest': values[-1] if values else 0,
                        'trend': 'increasing' if len(values) > 1 and values[-1] > values[0] else 'stable'
                    }
            
            return summary


class ObservabilityManager:
    """
    Comprehensive observability management for AA Kit.
    
    Features:
    - Metrics collection and aggregation
    - Distributed tracing
    - Performance monitoring
    - Structured logging
    - Real-time alerting
    """
    
    def __init__(self, service_name: str = "omniagent"):
        self.service_name = service_name
        self.metric_collector = MetricCollector()
        self.tracer = DistributedTracer(service_name)
        self.performance_monitor = PerformanceMonitor()
        
        # Component-specific metrics
        self._setup_default_metrics()
        
        # Background tasks
        self._metrics_task: Optional[asyncio.Task] = None
        self._start_background_tasks()
    
    def _setup_default_metrics(self):
        """Setup default performance thresholds."""
        # Response time thresholds
        self.performance_monitor.set_threshold('llm_response_time', 5.0, 10.0)
        self.performance_monitor.set_threshold('tool_execution_time', 3.0, 8.0)
        self.performance_monitor.set_threshold('agent_response_time', 10.0, 30.0)
        
        # Rate thresholds
        self.performance_monitor.set_threshold('error_rate', 5.0, 10.0)  # Percentage
        self.performance_monitor.set_threshold('timeout_rate', 2.0, 5.0)  # Percentage
    
    def _start_background_tasks(self):
        """Start background tasks for metrics aggregation."""
        if not self._metrics_task or self._metrics_task.done():
            self._metrics_task = asyncio.create_task(self._metrics_aggregation_loop())
    
    async def _metrics_aggregation_loop(self):
        """Background loop for metrics aggregation and cleanup."""
        while True:
            try:
                await asyncio.sleep(60)  # Aggregate every minute
                await self._aggregate_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics aggregation error: {e}")
    
    async def _aggregate_metrics(self):
        """Aggregate and process metrics."""
        # This could export to external systems like Prometheus, DataDog, etc.
        stats = self.get_comprehensive_stats()
        logger.info(f"Metrics aggregated: {json.dumps(stats, indent=2)}")
    
    # Metric recording methods
    def record_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Record a counter metric."""
        metric = MetricPoint(name, value, MetricType.COUNTER, tags=tags or {})
        self.metric_collector.record_metric(metric)
    
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a gauge metric."""
        metric = MetricPoint(name, value, MetricType.GAUGE, tags=tags or {})
        self.metric_collector.record_metric(metric)
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram metric."""
        metric = MetricPoint(name, value, MetricType.HISTOGRAM, tags=tags or {})
        self.metric_collector.record_metric(metric)
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record a timer metric."""
        metric = MetricPoint(name, duration, MetricType.TIMER, tags=tags or {})
        self.metric_collector.record_metric(metric)
        self.performance_monitor.record_performance(name, duration, tags)
    
    # Tracing methods
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, tags: Dict[str, str] = None):
        """Trace an operation with automatic timing."""
        start_time = time.time()
        
        async with self.tracer.trace_operation(operation_name, tags) as span:
            try:
                yield span
            finally:
                duration = time.time() - start_time
                self.record_timer(f"{operation_name}_duration", duration, tags)
    
    # High-level operation tracking
    async def track_llm_call(
        self,
        provider: str,
        model: str,
        tokens: int,
        duration: float,
        success: bool
    ):
        """Track LLM API call metrics."""
        tags = {'provider': provider, 'model': model}
        
        self.record_counter('llm_calls_total', 1, tags)
        self.record_timer('llm_response_time', duration, tags)
        self.record_histogram('llm_tokens', tokens, tags)
        
        if success:
            self.record_counter('llm_calls_success', 1, tags)
        else:
            self.record_counter('llm_calls_error', 1, tags)
    
    async def track_tool_execution(
        self,
        tool_name: str,
        duration: float,
        success: bool,
        error_type: Optional[str] = None
    ):
        """Track tool execution metrics."""
        tags = {'tool': tool_name}
        if error_type:
            tags['error_type'] = error_type
        
        self.record_counter('tool_executions_total', 1, tags)
        self.record_timer('tool_execution_time', duration, tags)
        
        if success:
            self.record_counter('tool_executions_success', 1, tags)
        else:
            self.record_counter('tool_executions_error', 1, tags)
    
    async def track_agent_interaction(
        self,
        agent_name: str,
        interaction_type: str,
        duration: float,
        success: bool
    ):
        """Track agent interaction metrics."""
        tags = {'agent': agent_name, 'type': interaction_type}
        
        self.record_counter('agent_interactions_total', 1, tags)
        self.record_timer('agent_response_time', duration, tags)
        
        if success:
            self.record_counter('agent_interactions_success', 1, tags)
        else:
            self.record_counter('agent_interactions_error', 1, tags)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive observability statistics."""
        return {
            'service': {
                'name': self.service_name,
                'uptime': time.time() - self.performance_monitor.start_time
            },
            'metrics': self.metric_collector.get_all_metrics(),
            'tracing': self.tracer.get_trace_stats(),
            'performance': self.performance_monitor.get_performance_summary(),
            'alerts': {
                'total': len(self.performance_monitor.alerts),
                'recent': [
                    a for a in self.performance_monitor.alerts 
                    if time.time() - a['timestamp'] < 300
                ]
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        stats = self.get_comprehensive_stats()
        
        # Determine health status
        recent_alerts = stats['alerts']['recent']
        critical_alerts = [a for a in recent_alerts if a['level'] == 'critical']
        
        if critical_alerts:
            status = 'unhealthy'
        elif recent_alerts:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'timestamp': time.time(),
            'uptime': stats['service']['uptime'],
            'alerts': len(recent_alerts),
            'critical_alerts': len(critical_alerts),
            'metrics_count': sum(
                m.get('total_points', 0) for m in stats['metrics'].values()
            ),
            'active_traces': stats['tracing']['active_spans']
        }
    
    async def close(self):
        """Close observability manager and cleanup resources."""
        if self._metrics_task and not self._metrics_task.done():
            self._metrics_task.cancel()
            try:
                await self._metrics_task
            except asyncio.CancelledError:
                pass


# Global observability manager
_global_observability_manager: Optional[ObservabilityManager] = None


def get_observability_manager() -> ObservabilityManager:
    """Get or create the global observability manager."""
    global _global_observability_manager
    
    if _global_observability_manager is None:
        _global_observability_manager = ObservabilityManager()
    
    return _global_observability_manager


# Convenience decorators and functions
def track_operation(operation_name: str, tags: Dict[str, str] = None):
    """Decorator to automatically track operation metrics."""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                obs = get_observability_manager()
                async with obs.trace_operation(operation_name, tags):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                obs = get_observability_manager()
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    obs.record_timer(f"{operation_name}_duration", duration, tags)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    obs.record_timer(f"{operation_name}_duration", duration, tags)
                    obs.record_counter(f"{operation_name}_errors", 1, tags)
                    raise
            return sync_wrapper
    return decorator


async def record_llm_metrics(provider: str, model: str, tokens: int, duration: float, success: bool):
    """Record LLM call metrics."""
    obs = get_observability_manager()
    await obs.track_llm_call(provider, model, tokens, duration, success)


async def record_tool_metrics(tool_name: str, duration: float, success: bool, error_type: str = None):
    """Record tool execution metrics."""
    obs = get_observability_manager()
    await obs.track_tool_execution(tool_name, duration, success, error_type)