"""
Enterprise-grade resource lifecycle management for AA Kit

Provides comprehensive resource management, cleanup tracking, and graceful shutdown
for all AA Kit components including agents, connections, and background tasks.
"""

import asyncio
import atexit
import logging
import signal
import threading
import time
import weakref
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Union
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceState(Enum):
    """Resource lifecycle states."""
    CREATED = "created"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class ShutdownPhase(Enum):
    """Shutdown phases for ordered cleanup."""
    IMMEDIATE = 0     # Background tasks, non-critical services
    NORMAL = 1        # Agents, tools, normal operations
    LATE = 2          # Connections, caches, critical infrastructure
    FINAL = 3         # Global managers, logging, system resources


@dataclass
class ResourceInfo:
    """Information about a managed resource."""
    
    resource_id: str
    resource_type: str
    state: ResourceState
    created_at: float
    shutdown_phase: ShutdownPhase
    cleanup_func: Optional[Callable[[], Awaitable[None]]]
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    last_activity: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def age(self) -> float:
        """Get resource age in seconds."""
        return time.time() - self.created_at
    
    @property
    def idle_time(self) -> float:
        """Get idle time since last activity."""
        return time.time() - self.last_activity


class ManagedResource(ABC):
    """Abstract base class for managed resources."""
    
    def __init__(self, resource_id: str, resource_type: str):
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.state = ResourceState.CREATED
        self._shutdown_callbacks: List[Callable[[], Awaitable[None]]] = []
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the resource."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up the resource."""
        pass
    
    def add_shutdown_callback(self, callback: Callable[[], Awaitable[None]]):
        """Add callback to be called during shutdown."""
        self._shutdown_callbacks.append(callback)
    
    async def shutdown(self):
        """Shutdown resource with callbacks."""
        self.state = ResourceState.STOPPING
        
        # Call shutdown callbacks in reverse order
        for callback in reversed(self._shutdown_callbacks):
            try:
                await callback()
            except Exception as e:
                logger.warning(f"Shutdown callback failed for {self.resource_id}: {e}")
        
        await self.cleanup()
        self.state = ResourceState.STOPPED


class ResourceManager:
    """
    Enterprise resource manager with dependency tracking and graceful shutdown.
    
    Features:
    - Resource lifecycle management
    - Dependency tracking and ordered shutdown
    - Graceful shutdown with configurable timeouts
    - Resource monitoring and cleanup
    - Signal handling for clean exits
    """
    
    def __init__(self, enable_signal_handlers: bool = True):
        self.resources: Dict[str, ResourceInfo] = {}
        self.weak_refs: Dict[str, Any] = {}  # Weak references to actual objects
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._shutdown_in_progress = False
        
        # Cleanup tracking
        self._cleanup_tasks: Set[asyncio.Task] = set()
        self._background_cleanup_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.cleanup_interval = 60.0  # Check for cleanup every minute
        self.idle_timeout = 300.0     # 5 minutes idle timeout
        self.shutdown_timeout = 30.0  # 30 seconds for graceful shutdown
        
        # Signal handling
        if enable_signal_handlers:
            self._setup_signal_handlers()
        
        # Register global cleanup
        atexit.register(self._sync_cleanup)
        
        # Start background cleanup
        self._start_background_cleanup()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.shutdown_all())
        
        # Handle common shutdown signals
        for sig in [signal.SIGINT, signal.SIGTERM]:
            try:
                signal.signal(sig, signal_handler)
            except (ValueError, OSError):
                # Signal handling might not be available (e.g., in threads)
                pass
    
    def _start_background_cleanup(self):
        """Start background task for periodic cleanup."""
        if not self._background_cleanup_task or self._background_cleanup_task.done():
            self._background_cleanup_task = asyncio.create_task(self._background_cleanup_loop())
    
    async def _background_cleanup_loop(self):
        """Background loop for cleaning up idle resources."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_idle_resources()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Background cleanup error: {e}")
    
    async def _cleanup_idle_resources(self):
        """Clean up resources that have been idle too long."""
        current_time = time.time()
        idle_resources = []
        
        async with self._lock:
            for resource_id, info in list(self.resources.items()):
                if (info.state == ResourceState.ACTIVE and 
                    current_time - info.last_activity > self.idle_timeout):
                    idle_resources.append(resource_id)
        
        # Clean up idle resources
        for resource_id in idle_resources:
            try:
                await self.cleanup_resource(resource_id, reason="idle_timeout")
                logger.debug(f"Cleaned up idle resource: {resource_id}")
            except Exception as e:
                logger.warning(f"Failed to cleanup idle resource {resource_id}: {e}")
    
    async def register_resource(
        self,
        resource: Union[ManagedResource, Any],
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        cleanup_func: Optional[Callable[[], Awaitable[None]]] = None,
        shutdown_phase: ShutdownPhase = ShutdownPhase.NORMAL,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """
        Register a resource for lifecycle management.
        
        Args:
            resource: The resource object to manage
            resource_id: Unique identifier (generated if None)
            resource_type: Type of resource for categorization
            cleanup_func: Custom cleanup function
            shutdown_phase: Phase during which to shutdown
            dependencies: List of resource IDs this depends on
            
        Returns:
            Resource ID
        """
        # Generate ID if not provided
        if resource_id is None:
            resource_id = f"{resource_type or 'resource'}_{id(resource)}_{int(time.time())}"
        
        # Determine resource type
        if resource_type is None:
            resource_type = type(resource).__name__
        
        # Get cleanup function
        if cleanup_func is None and hasattr(resource, 'cleanup'):
            cleanup_func = resource.cleanup
        elif cleanup_func is None and hasattr(resource, 'close'):
            cleanup_func = resource.close
        
        async with self._lock:
            # Create resource info
            info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                state=ResourceState.CREATED,
                created_at=time.time(),
                shutdown_phase=shutdown_phase,
                cleanup_func=cleanup_func,
                dependencies=set(dependencies or [])
            )
            
            # Store resource info and weak reference
            self.resources[resource_id] = info
            self.weak_refs[resource_id] = weakref.ref(resource, 
                                                    lambda ref: self._handle_resource_deletion(resource_id))
            
            # Update dependency graph
            for dep_id in info.dependencies:
                if dep_id in self.resources:
                    self.resources[dep_id].dependents.add(resource_id)
        
        logger.debug(f"Registered resource: {resource_id} ({resource_type})")
        return resource_id
    
    def _handle_resource_deletion(self, resource_id: str):
        """Handle when a resource is garbage collected."""
        asyncio.create_task(self._cleanup_deleted_resource(resource_id))
    
    async def _cleanup_deleted_resource(self, resource_id: str):
        """Clean up tracking for deleted resource."""
        async with self._lock:
            if resource_id in self.resources:
                info = self.resources[resource_id]
                info.state = ResourceState.STOPPED
                
                # Remove from dependency graph
                for dep_id in info.dependencies:
                    if dep_id in self.resources:
                        self.resources[dep_id].dependents.discard(resource_id)
                
                for dependent_id in info.dependents:
                    if dependent_id in self.resources:
                        self.resources[dependent_id].dependencies.discard(resource_id)
                
                # Clean up tracking
                del self.resources[resource_id]
                if resource_id in self.weak_refs:
                    del self.weak_refs[resource_id]
                
                logger.debug(f"Cleaned up deleted resource: {resource_id}")
    
    async def update_resource_activity(self, resource_id: str):
        """Update last activity time for a resource."""
        async with self._lock:
            if resource_id in self.resources:
                self.resources[resource_id].last_activity = time.time()
    
    async def set_resource_state(self, resource_id: str, state: ResourceState):
        """Set the state of a resource."""
        async with self._lock:
            if resource_id in self.resources:
                self.resources[resource_id].state = state
                logger.debug(f"Resource {resource_id} state changed to {state.value}")
    
    async def cleanup_resource(self, resource_id: str, reason: str = "manual"):
        """
        Clean up a specific resource.
        
        Args:
            resource_id: ID of resource to clean up
            reason: Reason for cleanup (for logging)
        """
        async with self._lock:
            if resource_id not in self.resources:
                return
            
            info = self.resources[resource_id]
            if info.state in [ResourceState.STOPPING, ResourceState.STOPPED]:
                return
            
            info.state = ResourceState.STOPPING
        
        logger.debug(f"Cleaning up resource {resource_id} (reason: {reason})")
        
        try:
            # Get the actual resource object
            resource_ref = self.weak_refs.get(resource_id)
            resource = resource_ref() if resource_ref else None
            
            # Call cleanup function
            if info.cleanup_func:
                await info.cleanup_func()
            elif resource and hasattr(resource, 'shutdown'):
                await resource.shutdown()
            
            # Update state
            await self.set_resource_state(resource_id, ResourceState.STOPPED)
            
        except Exception as e:
            logger.error(f"Error cleaning up resource {resource_id}: {e}")
            await self.set_resource_state(resource_id, ResourceState.ERROR)
            raise
    
    async def cleanup_by_type(self, resource_type: str):
        """Clean up all resources of a specific type."""
        resource_ids = []
        
        async with self._lock:
            resource_ids = [
                rid for rid, info in self.resources.items()
                if info.resource_type == resource_type and info.state == ResourceState.ACTIVE
            ]
        
        cleanup_tasks = [
            self.cleanup_resource(rid, f"type_cleanup:{resource_type}")
            for rid in resource_ids
        ]
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
    
    def _get_shutdown_order(self) -> List[List[str]]:
        """Get resources organized by shutdown phase and dependency order."""
        phases = {phase: [] for phase in ShutdownPhase}
        
        # Group by shutdown phase
        for resource_id, info in self.resources.items():
            if info.state == ResourceState.ACTIVE:
                phases[info.shutdown_phase].append(resource_id)
        
        # Sort each phase by dependency order (dependencies first)
        ordered_phases = []
        for phase in sorted(phases.keys(), key=lambda x: x.value):
            if phases[phase]:
                ordered = self._topological_sort(phases[phase])
                ordered_phases.append(ordered)
        
        return ordered_phases
    
    def _topological_sort(self, resource_ids: List[str]) -> List[str]:
        """Sort resources by dependency order (dependencies first)."""
        # Simple topological sort implementation
        in_degree = {rid: 0 for rid in resource_ids}
        
        # Calculate in-degrees
        for rid in resource_ids:
            info = self.resources[rid]
            for dep_id in info.dependencies:
                if dep_id in in_degree:
                    in_degree[rid] += 1
        
        # Process nodes with no dependencies first
        queue = [rid for rid, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degrees of dependents
            info = self.resources[current]
            for dependent_id in info.dependents:
                if dependent_id in in_degree:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)
        
        # Add any remaining resources (circular dependencies)
        remaining = set(resource_ids) - set(result)
        result.extend(remaining)
        
        return result
    
    async def shutdown_all(self, timeout: Optional[float] = None):
        """
        Shutdown all resources in dependency order.
        
        Args:
            timeout: Maximum time to wait for shutdown
        """
        if self._shutdown_in_progress:
            await self._shutdown_event.wait()
            return
        
        self._shutdown_in_progress = True
        shutdown_timeout = timeout or self.shutdown_timeout
        
        logger.info("Starting graceful shutdown of all resources")
        start_time = time.time()
        
        try:
            # Get shutdown order
            shutdown_phases = self._get_shutdown_order()
            
            # Shutdown each phase
            for phase_resources in shutdown_phases:
                if not phase_resources:
                    continue
                
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed >= shutdown_timeout:
                    logger.warning("Shutdown timeout exceeded, forcing cleanup")
                    break
                
                remaining_timeout = max(1.0, shutdown_timeout - elapsed)
                
                # Shutdown resources in this phase
                cleanup_tasks = [
                    self.cleanup_resource(rid, "graceful_shutdown")
                    for rid in phase_resources
                ]
                
                if cleanup_tasks:
                    try:
                        await asyncio.wait_for(
                            asyncio.gather(*cleanup_tasks, return_exceptions=True),
                            timeout=remaining_timeout
                        )
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout shutting down phase with {len(cleanup_tasks)} resources")
            
            # Cancel background tasks
            if self._background_cleanup_task:
                self._background_cleanup_task.cancel()
                try:
                    await self._background_cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel any remaining cleanup tasks
            for task in self._cleanup_tasks:
                if not task.done():
                    task.cancel()
            
            if self._cleanup_tasks:
                await asyncio.gather(*self._cleanup_tasks, return_exceptions=True)
            
            elapsed = time.time() - start_time
            logger.info(f"Graceful shutdown completed in {elapsed:.2f}s")
            
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
        finally:
            self._shutdown_event.set()
    
    def _sync_cleanup(self):
        """Synchronous cleanup for atexit handler."""
        if self._shutdown_in_progress:
            return
        
        try:
            # Try to run async cleanup
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                asyncio.create_task(self.shutdown_all())
            else:
                # Run cleanup directly
                loop.run_until_complete(self.shutdown_all())
        except Exception as e:
            logger.error(f"Error in sync cleanup: {e}")
    
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get statistics about managed resources."""
        stats = {
            'total_resources': len(self.resources),
            'by_state': {},
            'by_type': {},
            'by_phase': {},
            'oldest_resource_age': 0,
            'average_age': 0,
            'total_dependencies': 0
        }
        
        if not self.resources:
            return stats
        
        current_time = time.time()
        total_age = 0
        oldest_age = 0
        
        for info in self.resources.values():
            # Count by state
            state_key = info.state.value
            stats['by_state'][state_key] = stats['by_state'].get(state_key, 0) + 1
            
            # Count by type
            stats['by_type'][info.resource_type] = stats['by_type'].get(info.resource_type, 0) + 1
            
            # Count by phase
            phase_key = info.shutdown_phase.name
            stats['by_phase'][phase_key] = stats['by_phase'].get(phase_key, 0) + 1
            
            # Age calculations
            age = current_time - info.created_at
            total_age += age
            oldest_age = max(oldest_age, age)
            
            # Dependency count
            stats['total_dependencies'] += len(info.dependencies)
        
        stats['oldest_resource_age'] = round(oldest_age, 2)
        stats['average_age'] = round(total_age / len(self.resources), 2)
        
        return stats
    
    @asynccontextmanager
    async def managed_resource(
        self,
        resource: Any,
        resource_id: Optional[str] = None,
        cleanup_func: Optional[Callable[[], Awaitable[None]]] = None,
        **kwargs
    ):
        """
        Context manager for temporary resource management.
        
        Args:
            resource: Resource to manage
            resource_id: Optional resource ID
            cleanup_func: Optional cleanup function
            **kwargs: Additional registration parameters
        """
        registered_id = await self.register_resource(
            resource, resource_id, cleanup_func=cleanup_func, **kwargs
        )
        
        try:
            await self.set_resource_state(registered_id, ResourceState.ACTIVE)
            yield resource
        finally:
            await self.cleanup_resource(registered_id, "context_exit")


# Global resource manager instance
_global_resource_manager: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """Get or create the global resource manager."""
    global _global_resource_manager
    
    if _global_resource_manager is None:
        _global_resource_manager = ResourceManager()
    
    return _global_resource_manager


async def register_resource(
    resource: Any,
    resource_id: Optional[str] = None,
    **kwargs
) -> str:
    """Register a resource with the global manager."""
    manager = get_resource_manager()
    return await manager.register_resource(resource, resource_id, **kwargs)


async def cleanup_all_resources():
    """Clean up all resources using global manager."""
    global _global_resource_manager
    
    if _global_resource_manager:
        await _global_resource_manager.shutdown_all()


# Decorator for automatic resource management
def managed_resource(
    resource_type: Optional[str] = None,
    shutdown_phase: ShutdownPhase = ShutdownPhase.NORMAL,
    dependencies: Optional[List[str]] = None
):
    """
    Decorator to automatically register class instances as managed resources.
    
    Args:
        resource_type: Type name for the resource
        shutdown_phase: Shutdown phase
        dependencies: Resource dependencies
    """
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            # Register this instance
            manager = get_resource_manager()
            asyncio.create_task(
                manager.register_resource(
                    self,
                    resource_type=resource_type or cls.__name__,
                    shutdown_phase=shutdown_phase,
                    dependencies=dependencies
                )
            )
        
        cls.__init__ = new_init
        return cls
    
    return decorator