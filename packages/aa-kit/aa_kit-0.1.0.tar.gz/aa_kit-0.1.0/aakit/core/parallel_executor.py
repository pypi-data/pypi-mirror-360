"""
Enterprise-grade parallel execution for AA Kit

Implements concurrent execution for tools, agents, and multi-agent workflows
with load balancing, resource management, and failure isolation.
"""

import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Parallel execution strategies."""
    ALL_SUCCESS = "all_success"           # All must succeed
    FIRST_SUCCESS = "first_success"       # Return first success
    BEST_EFFORT = "best_effort"           # Return all results, including failures
    MAJORITY = "majority"                 # Majority must succeed
    FASTEST = "fastest"                   # Return fastest completion


class ExecutionMode(Enum):
    """Execution modes for different workloads."""
    IO_BOUND = "io_bound"                 # Async tasks (default)
    CPU_BOUND = "cpu_bound"               # Thread pool execution
    MIXED = "mixed"                       # Adaptive execution


@dataclass
class ExecutionConfig:
    """Configuration for parallel execution."""
    
    # Concurrency limits
    max_concurrent_tasks: int = 10
    max_concurrent_agents: int = 5
    max_concurrent_tools: int = 20
    
    # Execution strategy
    default_strategy: ExecutionStrategy = ExecutionStrategy.ALL_SUCCESS
    execution_mode: ExecutionMode = ExecutionMode.IO_BOUND
    
    # Timeouts
    task_timeout: float = 60.0
    total_timeout: float = 300.0
    
    # Resource management
    enable_load_balancing: bool = True
    enable_resource_monitoring: bool = True
    
    # Thread pool settings (for CPU-bound tasks)
    thread_pool_workers: Optional[int] = None
    
    # Failure handling
    max_retries: int = 3
    retry_delay: float = 1.0
    fail_fast: bool = False
    
    # Performance optimization
    enable_batching: bool = True
    batch_size: int = 50
    batch_timeout: float = 1.0


@dataclass
class TaskResult:
    """Result of a parallel task execution."""
    
    task_id: str
    success: bool
    result: Any = None
    exception: Optional[Exception] = None
    start_time: float = 0.0
    end_time: float = 0.0
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Get task duration."""
        return self.execution_time or (self.end_time - self.start_time)


@dataclass
class ExecutionResult:
    """Result of parallel execution."""
    
    strategy: ExecutionStrategy
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_duration: float
    results: List[TaskResult]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Get success rate percentage."""
        return (self.successful_tasks / self.total_tasks * 100) if self.total_tasks > 0 else 0
    
    @property
    def successful_results(self) -> List[TaskResult]:
        """Get only successful results."""
        return [r for r in self.results if r.success]
    
    @property
    def failed_results(self) -> List[TaskResult]:
        """Get only failed results."""
        return [r for r in self.results if not r.success]


class TaskExecutor(ABC):
    """Abstract base class for task executors."""
    
    @abstractmethod
    async def execute(
        self,
        tasks: List[Tuple[str, Callable[..., Awaitable[Any]], tuple, dict]],
        strategy: ExecutionStrategy,
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """Execute tasks with given strategy."""
        pass


class AsyncTaskExecutor(TaskExecutor):
    """Executor for async I/O-bound tasks."""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent_tasks)
    
    async def _execute_single_task(
        self,
        task_id: str,
        func: Callable[..., Awaitable[Any]],
        args: tuple,
        kwargs: dict,
        timeout: Optional[float] = None
    ) -> TaskResult:
        """Execute a single task with error handling."""
        start_time = time.time()
        
        try:
            async with self.semaphore:
                if timeout:
                    result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                else:
                    result = await func(*args, **kwargs)
                
                end_time = time.time()
                return TaskResult(
                    task_id=task_id,
                    success=True,
                    result=result,
                    start_time=start_time,
                    end_time=end_time,
                    execution_time=end_time - start_time
                )
                
        except Exception as e:
            end_time = time.time()
            return TaskResult(
                task_id=task_id,
                success=False,
                exception=e,
                start_time=start_time,
                end_time=end_time,
                execution_time=end_time - start_time
            )
    
    async def execute(
        self,
        tasks: List[Tuple[str, Callable[..., Awaitable[Any]], tuple, dict]],
        strategy: ExecutionStrategy,
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """Execute tasks with specified strategy."""
        start_time = time.time()
        total_tasks = len(tasks)
        
        if not tasks:
            return ExecutionResult(
                strategy=strategy,
                total_tasks=0,
                successful_tasks=0,
                failed_tasks=0,
                total_duration=0,
                results=[]
            )
        
        # Create task coroutines
        task_timeout = timeout or self.config.task_timeout
        task_coroutines = [
            self._execute_single_task(task_id, func, args, kwargs, task_timeout)
            for task_id, func, args, kwargs in tasks
        ]
        
        # Execute based on strategy
        results = await self._execute_with_strategy(task_coroutines, strategy, timeout)
        
        end_time = time.time()
        successful_tasks = sum(1 for r in results if r.success)
        failed_tasks = len(results) - successful_tasks
        
        return ExecutionResult(
            strategy=strategy,
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            total_duration=end_time - start_time,
            results=results
        )
    
    async def _execute_with_strategy(
        self,
        task_coroutines: List[Awaitable[TaskResult]],
        strategy: ExecutionStrategy,
        timeout: Optional[float]
    ) -> List[TaskResult]:
        """Execute coroutines with specified strategy."""
        
        if strategy == ExecutionStrategy.ALL_SUCCESS:
            return await self._execute_all_success(task_coroutines, timeout)
        elif strategy == ExecutionStrategy.FIRST_SUCCESS:
            return await self._execute_first_success(task_coroutines, timeout)
        elif strategy == ExecutionStrategy.BEST_EFFORT:
            return await self._execute_best_effort(task_coroutines, timeout)
        elif strategy == ExecutionStrategy.FASTEST:
            return await self._execute_fastest(task_coroutines, timeout)
        elif strategy == ExecutionStrategy.MAJORITY:
            return await self._execute_majority(task_coroutines, timeout)
        else:
            return await self._execute_best_effort(task_coroutines, timeout)
    
    async def _execute_all_success(
        self,
        task_coroutines: List[Awaitable[TaskResult]],
        timeout: Optional[float]
    ) -> List[TaskResult]:
        """Execute all tasks, fail if any fail."""
        try:
            if timeout:
                results = await asyncio.wait_for(
                    asyncio.gather(*task_coroutines),
                    timeout=timeout
                )
            else:
                results = await asyncio.gather(*task_coroutines)
            
            # Check if all succeeded
            if all(r.success for r in results):
                return results
            else:
                # If any failed, mark all as failed
                for result in results:
                    if result.success:
                        result.success = False
                        result.exception = Exception("Task failed due to ALL_SUCCESS strategy")
                return results
                
        except asyncio.TimeoutError:
            # Return timeout results
            return [
                TaskResult(f"task_{i}", False, exception=asyncio.TimeoutError("Total timeout exceeded"))
                for i in range(len(task_coroutines))
            ]
    
    async def _execute_first_success(
        self,
        task_coroutines: List[Awaitable[TaskResult]],
        timeout: Optional[float]
    ) -> List[TaskResult]:
        """Return first successful result."""
        pending = set(asyncio.create_task(coro) for coro in task_coroutines)
        results = []
        
        try:
            while pending:
                done, pending = await asyncio.wait(
                    pending,
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=timeout
                )
                
                for task in done:
                    result = await task
                    results.append(result)
                    
                    if result.success:
                        # Cancel remaining tasks
                        for remaining_task in pending:
                            remaining_task.cancel()
                        
                        # Add cancelled results
                        for i in range(len(pending)):
                            results.append(TaskResult(
                                f"cancelled_{i}",
                                False,
                                exception=asyncio.CancelledError("Cancelled due to first success")
                            ))
                        
                        return results
                
                if timeout and time.time() > timeout:
                    break
            
            # No success found
            return results
            
        except asyncio.TimeoutError:
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            return results
    
    async def _execute_best_effort(
        self,
        task_coroutines: List[Awaitable[TaskResult]],
        timeout: Optional[float]
    ) -> List[TaskResult]:
        """Execute all tasks, return all results regardless of success/failure."""
        try:
            if timeout:
                done, pending = await asyncio.wait(
                    task_coroutines,
                    timeout=timeout,
                    return_when=asyncio.ALL_COMPLETED
                )
                
                results = []
                for task in done:
                    results.append(await task)
                
                # Handle pending (timed out) tasks
                for i, task in enumerate(pending):
                    task.cancel()
                    results.append(TaskResult(
                        f"timeout_{i}",
                        False,
                        exception=asyncio.TimeoutError("Task timeout")
                    ))
                
                return results
            else:
                return await asyncio.gather(*task_coroutines, return_exceptions=False)
                
        except Exception as e:
            # This shouldn't happen with return_exceptions=False, but just in case
            return [TaskResult("error", False, exception=e)]
    
    async def _execute_fastest(
        self,
        task_coroutines: List[Awaitable[TaskResult]],
        timeout: Optional[float]
    ) -> List[TaskResult]:
        """Return the fastest completing task."""
        try:
            done, pending = await asyncio.wait(
                task_coroutines,
                return_when=asyncio.FIRST_COMPLETED,
                timeout=timeout
            )
            
            # Get the first completed result
            fastest_result = await next(iter(done))
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            
            return [fastest_result]
            
        except asyncio.TimeoutError:
            return [TaskResult("timeout", False, exception=asyncio.TimeoutError("No task completed in time"))]
    
    async def _execute_majority(
        self,
        task_coroutines: List[Awaitable[TaskResult]],
        timeout: Optional[float]
    ) -> List[TaskResult]:
        """Execute until majority succeeds or fails."""
        total_tasks = len(task_coroutines)
        majority_threshold = (total_tasks // 2) + 1
        
        pending = set(asyncio.create_task(coro) for coro in task_coroutines)
        results = []
        successful_count = 0
        
        try:
            while pending and successful_count < majority_threshold:
                done, pending = await asyncio.wait(
                    pending,
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=timeout
                )
                
                for task in done:
                    result = await task
                    results.append(result)
                    
                    if result.success:
                        successful_count += 1
                        
                        if successful_count >= majority_threshold:
                            # Cancel remaining tasks
                            for remaining_task in pending:
                                remaining_task.cancel()
                            break
            
            return results
            
        except asyncio.TimeoutError:
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
            return results


class ThreadPoolTaskExecutor(TaskExecutor):
    """Executor for CPU-bound tasks using thread pool."""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        # Get CPU count in a cross-platform way
        try:
            cpu_count = len(os.sched_getaffinity(0))
        except AttributeError:
            # macOS doesn't have sched_getaffinity
            cpu_count = os.cpu_count() or 4
        
        self.thread_pool = ThreadPoolExecutor(
            max_workers=config.thread_pool_workers or min(32, cpu_count + 4)
        )
    
    async def execute(
        self,
        tasks: List[Tuple[str, Callable[..., Any], tuple, dict]],
        strategy: ExecutionStrategy,
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """Execute CPU-bound tasks in thread pool."""
        start_time = time.time()
        
        # Convert sync tasks to async
        async_tasks = []
        for task_id, func, args, kwargs in tasks:
            async def wrapper():
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(self.thread_pool, lambda: func(*args, **kwargs))
            
            async_tasks.append((task_id, wrapper, (), {}))
        
        # Use async executor for the rest
        async_executor = AsyncTaskExecutor(self.config)
        return await async_executor.execute(async_tasks, strategy, timeout)


class ParallelExecutor:
    """
    Enterprise-grade parallel execution manager.
    
    Features:
    - Multiple execution strategies (all success, first success, best effort, etc.)
    - Support for both I/O-bound and CPU-bound tasks
    - Resource management and load balancing
    - Comprehensive monitoring and statistics
    """
    
    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        
        # Create executors
        self.async_executor = AsyncTaskExecutor(self.config)
        self.thread_pool_executor = ThreadPoolTaskExecutor(self.config)
        
        # Statistics
        self.stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_tasks': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'average_execution_time': 0.0,
            'average_task_time': 0.0
        }
    
    def _get_executor(self, execution_mode: ExecutionMode) -> TaskExecutor:
        """Get appropriate executor based on execution mode."""
        if execution_mode == ExecutionMode.CPU_BOUND:
            return self.thread_pool_executor
        else:
            return self.async_executor
    
    async def execute_functions(
        self,
        functions: List[Tuple[str, Callable[..., Any], tuple, dict]],
        strategy: Optional[ExecutionStrategy] = None,
        execution_mode: Optional[ExecutionMode] = None,
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """
        Execute multiple functions in parallel.
        
        Args:
            functions: List of (task_id, function, args, kwargs) tuples
            strategy: Execution strategy
            execution_mode: Execution mode (I/O vs CPU bound)
            timeout: Total execution timeout
            
        Returns:
            ExecutionResult with all task results
        """
        strategy = strategy or self.config.default_strategy
        execution_mode = execution_mode or self.config.execution_mode
        timeout = timeout or self.config.total_timeout
        
        # Get appropriate executor
        executor = self._get_executor(execution_mode)
        
        # Execute tasks
        start_time = time.time()
        result = await executor.execute(functions, strategy, timeout)
        
        # Update statistics
        self._update_stats(result, time.time() - start_time)
        
        return result
    
    async def execute_tool_calls(
        self,
        tool_calls: List[Tuple[str, Callable[..., Awaitable[Any]], list, dict]],
        strategy: Optional[ExecutionStrategy] = None,
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """
        Execute multiple tool calls in parallel.
        
        Args:
            tool_calls: List of (tool_name, tool_function, args, kwargs) tuples
            strategy: Execution strategy
            timeout: Total execution timeout
            
        Returns:
            ExecutionResult with all tool results
        """
        # Convert to function format
        functions = [
            (tool_name, tool_func, tuple(args), kwargs)
            for tool_name, tool_func, args, kwargs in tool_calls
        ]
        
        return await self.execute_functions(
            functions,
            strategy=strategy or ExecutionStrategy.BEST_EFFORT,
            execution_mode=ExecutionMode.IO_BOUND,
            timeout=timeout
        )
    
    async def execute_agent_calls(
        self,
        agent_calls: List[Tuple[str, Callable[..., Awaitable[Any]], str, dict]],
        strategy: Optional[ExecutionStrategy] = None,
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """
        Execute multiple agent calls in parallel.
        
        Args:
            agent_calls: List of (agent_name, agent_chat_func, message, kwargs) tuples
            strategy: Execution strategy
            timeout: Total execution timeout
            
        Returns:
            ExecutionResult with all agent results
        """
        # Apply agent-specific concurrency limit
        original_limit = self.config.max_concurrent_tasks
        self.config.max_concurrent_tasks = min(
            self.config.max_concurrent_agents,
            self.config.max_concurrent_tasks
        )
        
        try:
            # Convert to function format
            functions = [
                (agent_name, agent_func, (message,), kwargs)
                for agent_name, agent_func, message, kwargs in agent_calls
            ]
            
            return await self.execute_functions(
                functions,
                strategy=strategy or ExecutionStrategy.BEST_EFFORT,
                execution_mode=ExecutionMode.IO_BOUND,
                timeout=timeout
            )
        finally:
            # Restore original limit
            self.config.max_concurrent_tasks = original_limit
    
    async def map_async(
        self,
        func: Callable[..., Awaitable[Any]],
        items: List[Any],
        strategy: Optional[ExecutionStrategy] = None,
        timeout: Optional[float] = None,
        batch_size: Optional[int] = None
    ) -> ExecutionResult:
        """
        Map an async function over a list of items in parallel.
        
        Args:
            func: Async function to apply
            items: List of items to process
            strategy: Execution strategy
            timeout: Total execution timeout
            batch_size: Batch size for processing
            
        Returns:
            ExecutionResult with all mapped results
        """
        batch_size = batch_size or self.config.batch_size
        
        # Create function calls
        functions = [
            (f"item_{i}", func, (item,), {})
            for i, item in enumerate(items)
        ]
        
        # Process in batches if needed
        if len(functions) <= batch_size:
            return await self.execute_functions(functions, strategy, timeout=timeout)
        
        # Batch processing
        all_results = []
        for i in range(0, len(functions), batch_size):
            batch = functions[i:i + batch_size]
            batch_result = await self.execute_functions(batch, strategy, timeout=timeout)
            all_results.extend(batch_result.results)
        
        # Combine results
        successful_tasks = sum(1 for r in all_results if r.success)
        failed_tasks = len(all_results) - successful_tasks
        
        return ExecutionResult(
            strategy=strategy or self.config.default_strategy,
            total_tasks=len(all_results),
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            total_duration=sum(r.duration for r in all_results),
            results=all_results
        )
    
    def _update_stats(self, result: ExecutionResult, execution_time: float):
        """Update execution statistics."""
        self.stats['total_executions'] += 1
        self.stats['total_tasks'] += result.total_tasks
        self.stats['successful_tasks'] += result.successful_tasks
        self.stats['failed_tasks'] += result.failed_tasks
        
        if result.successful_tasks > 0:
            self.stats['successful_executions'] += 1
        else:
            self.stats['failed_executions'] += 1
        
        # Update averages
        total_execs = self.stats['total_executions']
        current_avg_exec = self.stats['average_execution_time']
        new_avg_exec = (current_avg_exec * (total_execs - 1) + execution_time) / total_execs
        self.stats['average_execution_time'] = new_avg_exec
        
        if result.results:
            avg_task_time = sum(r.duration for r in result.results) / len(result.results)
            total_tasks = self.stats['total_tasks']
            current_avg_task = self.stats['average_task_time']
            new_avg_task = (current_avg_task * (total_tasks - result.total_tasks) + 
                          avg_task_time * result.total_tasks) / total_tasks
            self.stats['average_task_time'] = new_avg_task
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics."""
        total_execs = self.stats['total_executions']
        success_rate = (self.stats['successful_executions'] / total_execs * 100) if total_execs > 0 else 0
        
        total_tasks = self.stats['total_tasks']
        task_success_rate = (self.stats['successful_tasks'] / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'executions': {
                'total': total_execs,
                'successful': self.stats['successful_executions'],
                'failed': self.stats['failed_executions'],
                'success_rate_percent': round(success_rate, 2),
                'average_duration': round(self.stats['average_execution_time'], 3)
            },
            'tasks': {
                'total': total_tasks,
                'successful': self.stats['successful_tasks'],
                'failed': self.stats['failed_tasks'],
                'success_rate_percent': round(task_success_rate, 2),
                'average_duration': round(self.stats['average_task_time'], 3)
            },
            'configuration': {
                'max_concurrent_tasks': self.config.max_concurrent_tasks,
                'max_concurrent_agents': self.config.max_concurrent_agents,
                'default_strategy': self.config.default_strategy.value,
                'execution_mode': self.config.execution_mode.value
            }
        }
    
    async def close(self):
        """Close executor and cleanup resources."""
        if hasattr(self.thread_pool_executor, 'thread_pool'):
            self.thread_pool_executor.thread_pool.shutdown(wait=True)


# Global parallel executor instance
_global_parallel_executor: Optional[ParallelExecutor] = None


def get_parallel_executor() -> ParallelExecutor:
    """Get or create the global parallel executor instance."""
    global _global_parallel_executor
    
    if _global_parallel_executor is None:
        _global_parallel_executor = ParallelExecutor()
    
    return _global_parallel_executor


async def execute_parallel(
    functions: List[Tuple[str, Callable[..., Any], tuple, dict]],
    strategy: ExecutionStrategy = ExecutionStrategy.ALL_SUCCESS,
    timeout: Optional[float] = None
) -> ExecutionResult:
    """
    Convenient function for parallel execution.
    
    Args:
        functions: List of (id, function, args, kwargs) tuples
        strategy: Execution strategy
        timeout: Total timeout
        
    Returns:
        ExecutionResult
    """
    executor = get_parallel_executor()
    return await executor.execute_functions(functions, strategy, timeout=timeout)