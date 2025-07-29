"""
Enterprise-grade streaming implementation for AA Kit

Provides real-time streaming for LLM responses, agent reasoning, and multi-agent
communications with backpressure handling and WebSocket support.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Union
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Types of streaming data."""
    TOKEN = "token"                    # Individual tokens
    CHUNK = "chunk"                    # Text chunks
    REASONING = "reasoning"            # Reasoning steps
    TOOL_CALL = "tool_call"           # Tool execution
    AGENT_STATE = "agent_state"       # Agent state changes
    ERROR = "error"                   # Error messages
    METADATA = "metadata"             # Metadata updates
    COMPLETION = "completion"         # Stream completion


class StreamFormat(Enum):
    """Stream output formats."""
    RAW = "raw"                       # Raw data
    JSON = "json"                     # JSON formatted
    SSE = "sse"                       # Server-Sent Events
    WEBSOCKET = "websocket"           # WebSocket messages


@dataclass
class StreamChunk:
    """A single chunk of streaming data."""
    
    id: str
    type: StreamType
    data: Any
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    sequence: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'type': self.type.value,
            'data': self.data,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'sequence': self.sequence
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    def to_sse(self) -> str:
        """Convert to Server-Sent Events format."""
        lines = [
            f"id: {self.id}",
            f"event: {self.type.value}",
            f"data: {json.dumps(self.data)}"
        ]
        if self.metadata:
            lines.append(f"metadata: {json.dumps(self.metadata)}")
        return '\n'.join(lines) + '\n\n'


class StreamBuffer:
    """Buffer for managing streaming data with backpressure."""
    
    def __init__(self, max_size: int = 1000, max_memory: int = 10 * 1024 * 1024):
        self.max_size = max_size
        self.max_memory = max_memory
        self.buffer: asyncio.Queue = asyncio.Queue(maxsize=max_size)
        self.current_memory = 0
        self.dropped_chunks = 0
        self.total_chunks = 0
        self._lock = asyncio.Lock()
    
    async def put(self, chunk: StreamChunk) -> bool:
        """
        Add chunk to buffer with backpressure handling.
        
        Returns:
            True if chunk was added, False if dropped due to backpressure
        """
        chunk_size = len(json.dumps(chunk.to_dict()).encode())
        
        async with self._lock:
            # Check memory limit
            if self.current_memory + chunk_size > self.max_memory:
                self.dropped_chunks += 1
                return False
            
            try:
                # Try to put with immediate timeout (non-blocking)
                self.buffer.put_nowait(chunk)
                self.current_memory += chunk_size
                self.total_chunks += 1
                return True
            except asyncio.QueueFull:
                self.dropped_chunks += 1
                return False
    
    async def get(self) -> Optional[StreamChunk]:
        """Get next chunk from buffer."""
        try:
            chunk = await self.buffer.get()
            async with self._lock:
                chunk_size = len(json.dumps(chunk.to_dict()).encode())
                self.current_memory -= chunk_size
            return chunk
        except asyncio.CancelledError:
            return None
    
    async def get_nowait(self) -> Optional[StreamChunk]:
        """Get chunk without waiting."""
        try:
            chunk = self.buffer.get_nowait()
            async with self._lock:
                chunk_size = len(json.dumps(chunk.to_dict()).encode())
                self.current_memory -= chunk_size
            return chunk
        except asyncio.QueueEmpty:
            return None
    
    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return self.buffer.empty()
    
    def size(self) -> int:
        """Get current buffer size."""
        return self.buffer.qsize()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        return {
            'buffer_size': self.size(),
            'max_size': self.max_size,
            'current_memory': self.current_memory,
            'max_memory': self.max_memory,
            'total_chunks': self.total_chunks,
            'dropped_chunks': self.dropped_chunks,
            'drop_rate': self.dropped_chunks / max(1, self.total_chunks) * 100
        }


class StreamProcessor(ABC):
    """Abstract base class for stream processors."""
    
    @abstractmethod
    async def process_chunk(self, chunk: StreamChunk) -> Optional[StreamChunk]:
        """Process a stream chunk and optionally transform it."""
        pass


class TokenAggregator(StreamProcessor):
    """Aggregates individual tokens into larger chunks."""
    
    def __init__(self, chunk_size: int = 50, flush_timeout: float = 0.5):
        self.chunk_size = chunk_size
        self.flush_timeout = flush_timeout
        self.buffer = []
        self.last_flush = time.time()
    
    async def process_chunk(self, chunk: StreamChunk) -> Optional[StreamChunk]:
        """Aggregate tokens into chunks."""
        if chunk.type != StreamType.TOKEN:
            return chunk
        
        self.buffer.append(chunk.data)
        current_time = time.time()
        
        # Flush if buffer is full or timeout exceeded
        if (len(self.buffer) >= self.chunk_size or 
            current_time - self.last_flush >= self.flush_timeout):
            
            aggregated_data = ''.join(self.buffer)
            self.buffer.clear()
            self.last_flush = current_time
            
            return StreamChunk(
                id=str(uuid.uuid4()),
                type=StreamType.CHUNK,
                data=aggregated_data,
                metadata={'aggregated_tokens': len(self.buffer)}
            )
        
        return None


class ReasoningTracker(StreamProcessor):
    """Tracks and enhances reasoning steps."""
    
    def __init__(self):
        self.reasoning_steps = []
        self.current_step = 0
    
    async def process_chunk(self, chunk: StreamChunk) -> Optional[StreamChunk]:
        """Enhance reasoning chunks with step tracking."""
        if chunk.type == StreamType.REASONING:
            self.current_step += 1
            self.reasoning_steps.append(chunk.data)
            
            # Enhance with step information
            enhanced_chunk = StreamChunk(
                id=chunk.id,
                type=chunk.type,
                data=chunk.data,
                timestamp=chunk.timestamp,
                metadata={
                    **chunk.metadata,
                    'step_number': self.current_step,
                    'total_steps': len(self.reasoning_steps)
                }
            )
            return enhanced_chunk
        
        return chunk


class StreamManager:
    """
    Enterprise-grade streaming manager for real-time data delivery.
    
    Features:
    - Multiple stream types and formats
    - Backpressure handling and buffering
    - Stream processing and transformation
    - WebSocket and SSE support
    - Performance monitoring and statistics
    """
    
    def __init__(
        self,
        buffer_size: int = 1000,
        max_memory: int = 10 * 1024 * 1024,
        enable_processing: bool = True
    ):
        self.buffer = StreamBuffer(buffer_size, max_memory)
        self.processors: List[StreamProcessor] = []
        self.subscribers: Dict[str, asyncio.Queue] = {}
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self._sequence_counter = 0
        self._lock = asyncio.Lock()
        
        # Default processors
        if enable_processing:
            self.processors.extend([
                TokenAggregator(),
                ReasoningTracker()
            ])
        
        # Statistics
        self.stats = {
            'total_chunks': 0,
            'chunks_by_type': {},
            'active_subscribers': 0,
            'active_streams': 0,
            'bytes_streamed': 0
        }
    
    def add_processor(self, processor: StreamProcessor):
        """Add a stream processor."""
        self.processors.append(processor)
    
    async def create_stream(
        self,
        stream_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new stream.
        
        Args:
            stream_id: Optional stream identifier
            metadata: Stream metadata
            
        Returns:
            Stream ID
        """
        if stream_id is None:
            stream_id = str(uuid.uuid4())
        
        async with self._lock:
            self.active_streams[stream_id] = {
                'created_at': time.time(),
                'metadata': metadata or {},
                'chunk_count': 0,
                'bytes_sent': 0
            }
            self.stats['active_streams'] = len(self.active_streams)
        
        logger.debug(f"Created stream: {stream_id}")
        return stream_id
    
    async def emit(
        self,
        stream_id: str,
        chunk_type: StreamType,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Emit data to a stream.
        
        Args:
            stream_id: Stream identifier
            chunk_type: Type of data being streamed
            data: The data to stream
            metadata: Additional metadata
            
        Returns:
            True if emitted successfully, False if dropped
        """
        if stream_id not in self.active_streams:
            logger.warning(f"Attempted to emit to non-existent stream: {stream_id}")
            return False
        
        # Create chunk
        chunk = StreamChunk(
            id=str(uuid.uuid4()),
            type=chunk_type,
            data=data,
            metadata={
                'stream_id': stream_id,
                **(metadata or {})
            },
            sequence=self._get_next_sequence()
        )
        
        # Process chunk through processors
        processed_chunk = chunk
        for processor in self.processors:
            result = await processor.process_chunk(processed_chunk)
            if result is not None:
                processed_chunk = result
        
        # Add to buffer
        success = await self.buffer.put(processed_chunk)
        
        if success:
            # Update statistics
            async with self._lock:
                self.stats['total_chunks'] += 1
                self.stats['chunks_by_type'][chunk_type.value] = (
                    self.stats['chunks_by_type'].get(chunk_type.value, 0) + 1
                )
                
                stream_info = self.active_streams[stream_id]
                stream_info['chunk_count'] += 1
                
                chunk_size = len(json.dumps(processed_chunk.to_dict()).encode())
                stream_info['bytes_sent'] += chunk_size
                self.stats['bytes_streamed'] += chunk_size
        
        return success
    
    def _get_next_sequence(self) -> int:
        """Get next sequence number."""
        self._sequence_counter += 1
        return self._sequence_counter
    
    async def subscribe(
        self,
        subscriber_id: str,
        stream_id: Optional[str] = None,
        chunk_types: Optional[List[StreamType]] = None
    ) -> AsyncIterator[StreamChunk]:
        """
        Subscribe to stream data.
        
        Args:
            subscriber_id: Unique subscriber identifier
            stream_id: Specific stream to subscribe to (None for all)
            chunk_types: Specific chunk types to receive (None for all)
            
        Yields:
            StreamChunk objects
        """
        subscriber_queue = asyncio.Queue(maxsize=100)
        
        async with self._lock:
            self.subscribers[subscriber_id] = subscriber_queue
            self.stats['active_subscribers'] = len(self.subscribers)
        
        logger.debug(f"Subscriber {subscriber_id} subscribed to stream {stream_id}")
        
        try:
            # Start delivery task
            delivery_task = asyncio.create_task(
                self._deliver_to_subscriber(
                    subscriber_id, subscriber_queue, stream_id, chunk_types
                )
            )
            
            # Yield chunks from subscriber queue
            while True:
                try:
                    chunk = await asyncio.wait_for(subscriber_queue.get(), timeout=1.0)
                    if chunk is None:  # Termination signal
                        break
                    yield chunk
                except asyncio.TimeoutError:
                    # Check if delivery task is still running
                    if delivery_task.done():
                        break
                    continue
        
        finally:
            # Cleanup
            delivery_task.cancel()
            async with self._lock:
                if subscriber_id in self.subscribers:
                    del self.subscribers[subscriber_id]
                self.stats['active_subscribers'] = len(self.subscribers)
            
            logger.debug(f"Subscriber {subscriber_id} unsubscribed")
    
    async def _deliver_to_subscriber(
        self,
        subscriber_id: str,
        subscriber_queue: asyncio.Queue,
        stream_id: Optional[str],
        chunk_types: Optional[List[StreamType]]
    ):
        """Deliver chunks to a specific subscriber."""
        while subscriber_id in self.subscribers:
            try:
                # Get chunk from main buffer
                chunk = await asyncio.wait_for(self.buffer.get(), timeout=1.0)
                if chunk is None:
                    continue
                
                # Filter by stream ID if specified
                if stream_id and chunk.metadata.get('stream_id') != stream_id:
                    continue
                
                # Filter by chunk types if specified
                if chunk_types and chunk.type not in chunk_types:
                    continue
                
                # Try to deliver to subscriber
                try:
                    subscriber_queue.put_nowait(chunk)
                except asyncio.QueueFull:
                    # Subscriber is too slow, drop chunk
                    logger.warning(f"Dropping chunk for slow subscriber: {subscriber_id}")
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error delivering to subscriber {subscriber_id}: {e}")
                break
        
        # Send termination signal
        try:
            subscriber_queue.put_nowait(None)
        except asyncio.QueueFull:
            pass
    
    async def stream_iterator(
        self,
        stream_id: str,
        format: StreamFormat = StreamFormat.RAW,
        chunk_types: Optional[List[StreamType]] = None
    ) -> AsyncIterator[Union[StreamChunk, str, bytes]]:
        """
        Get an iterator for stream data in specified format.
        
        Args:
            stream_id: Stream to iterate over
            format: Output format
            chunk_types: Types of chunks to include
            
        Yields:
            Formatted stream data
        """
        subscriber_id = f"iterator_{stream_id}_{uuid.uuid4()}"
        
        async for chunk in self.subscribe(subscriber_id, stream_id, chunk_types):
            if format == StreamFormat.RAW:
                yield chunk
            elif format == StreamFormat.JSON:
                yield chunk.to_json()
            elif format == StreamFormat.SSE:
                yield chunk.to_sse()
            elif format == StreamFormat.WEBSOCKET:
                yield json.dumps({
                    'type': 'stream_chunk',
                    'data': chunk.to_dict()
                })
    
    async def close_stream(self, stream_id: str):
        """Close a specific stream."""
        async with self._lock:
            if stream_id in self.active_streams:
                # Emit completion chunk
                await self.emit(
                    stream_id,
                    StreamType.COMPLETION,
                    {'status': 'completed'},
                    {'final': True}
                )
                
                del self.active_streams[stream_id]
                self.stats['active_streams'] = len(self.active_streams)
                
                logger.debug(f"Closed stream: {stream_id}")
    
    async def close_all_streams(self):
        """Close all active streams."""
        stream_ids = list(self.active_streams.keys())
        for stream_id in stream_ids:
            await self.close_stream(stream_id)
    
    def get_stream_stats(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific stream."""
        if stream_id not in self.active_streams:
            return None
        
        stream_info = self.active_streams[stream_id]
        current_time = time.time()
        
        return {
            'stream_id': stream_id,
            'created_at': stream_info['created_at'],
            'age_seconds': current_time - stream_info['created_at'],
            'chunk_count': stream_info['chunk_count'],
            'bytes_sent': stream_info['bytes_sent'],
            'metadata': stream_info['metadata']
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global streaming statistics."""
        buffer_stats = self.buffer.get_stats()
        
        return {
            'streams': {
                'active_count': self.stats['active_streams'],
                'total_chunks': self.stats['total_chunks'],
                'bytes_streamed': self.stats['bytes_streamed'],
                'chunks_by_type': self.stats['chunks_by_type']
            },
            'subscribers': {
                'active_count': self.stats['active_subscribers']
            },
            'buffer': buffer_stats,
            'performance': {
                'average_chunk_size': (
                    self.stats['bytes_streamed'] / max(1, self.stats['total_chunks'])
                ),
                'buffer_utilization': buffer_stats['buffer_size'] / buffer_stats['max_size'] * 100
            }
        }


# WebSocket streaming helper
class WebSocketStreamer:
    """Helper for streaming over WebSocket connections."""
    
    def __init__(self, websocket, stream_manager: StreamManager):
        self.websocket = websocket
        self.stream_manager = stream_manager
        self.subscriber_id = f"ws_{id(websocket)}"
    
    async def stream_to_websocket(
        self,
        stream_id: str,
        chunk_types: Optional[List[StreamType]] = None
    ):
        """Stream data to WebSocket connection."""
        try:
            async for message in self.stream_manager.stream_iterator(
                stream_id, StreamFormat.WEBSOCKET, chunk_types
            ):
                await self.websocket.send(message)
        except Exception as e:
            logger.error(f"WebSocket streaming error: {e}")
            # Send error message
            error_msg = json.dumps({
                'type': 'error',
                'message': str(e)
            })
            try:
                await self.websocket.send(error_msg)
            except:
                pass


# Server-Sent Events streaming helper
class SSEStreamer:
    """Helper for streaming over Server-Sent Events."""
    
    def __init__(self, stream_manager: StreamManager):
        self.stream_manager = stream_manager
    
    async def stream_response(
        self,
        stream_id: str,
        chunk_types: Optional[List[StreamType]] = None
    ) -> AsyncIterator[str]:
        """Generate SSE response."""
        # Send initial headers (to be used by web framework)
        yield "data: " + json.dumps({"type": "stream_start", "stream_id": stream_id}) + "\n\n"
        
        try:
            async for sse_data in self.stream_manager.stream_iterator(
                stream_id, StreamFormat.SSE, chunk_types
            ):
                yield sse_data
        except Exception as e:
            error_data = f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            yield error_data
        finally:
            # Send completion event
            yield "data: " + json.dumps({"type": "stream_end"}) + "\n\n"


# Global stream manager instance
_global_stream_manager: Optional[StreamManager] = None


def get_stream_manager() -> StreamManager:
    """Get or create the global stream manager instance."""
    global _global_stream_manager
    
    if _global_stream_manager is None:
        _global_stream_manager = StreamManager()
    
    return _global_stream_manager


# Convenience functions
async def emit_token(stream_id: str, token: str) -> bool:
    """Emit a single token to stream."""
    manager = get_stream_manager()
    return await manager.emit(stream_id, StreamType.TOKEN, token)


async def emit_reasoning(stream_id: str, reasoning: str) -> bool:
    """Emit reasoning step to stream."""
    manager = get_stream_manager()
    return await manager.emit(stream_id, StreamType.REASONING, reasoning)


async def emit_tool_call(stream_id: str, tool_name: str, args: Dict[str, Any]) -> bool:
    """Emit tool call to stream."""
    manager = get_stream_manager()
    return await manager.emit(
        stream_id, 
        StreamType.TOOL_CALL, 
        {'tool': tool_name, 'args': args}
    )