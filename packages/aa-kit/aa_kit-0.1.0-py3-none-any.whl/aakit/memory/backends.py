"""
Memory Backend Implementations

Pluggable memory backends for storing conversation history and agent state.
"""

import asyncio
import json
import sqlite3
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import aiosqlite
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

from ..core.exceptions import MemoryError, MemoryConnectionError


@dataclass
class MemoryRecord:
    """Represents a single memory record."""
    session_id: str
    timestamp: float
    role: str  # "user", "assistant", "system"
    content: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryRecord':
        """Create from dictionary."""
        return cls(**data)


class MemoryBackend(ABC):
    """Abstract base class for memory backends."""
    
    @abstractmethod
    async def store(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a memory record."""
        pass
    
    @abstractmethod
    async def retrieve(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """Retrieve memory records for a session."""
        pass
    
    @abstractmethod
    async def clear(self, session_id: str) -> None:
        """Clear all memory for a session."""
        pass
    
    @abstractmethod
    async def get_sessions(self) -> List[str]:
        """Get list of all session IDs."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the backend connection."""
        pass


class InMemoryBackend(MemoryBackend):
    """In-memory backend for development and testing."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self.storage: Dict[str, List[MemoryRecord]] = {}
    
    async def store(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a memory record in memory."""
        if session_id not in self.storage:
            self.storage[session_id] = []
        
        record = MemoryRecord(
            session_id=session_id,
            timestamp=time.time(),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.storage[session_id].append(record)
    
    async def retrieve(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """Retrieve memory records from memory."""
        if session_id not in self.storage:
            return []
        
        records = self.storage[session_id]
        
        # Apply offset and limit
        if offset > 0:
            records = records[offset:]
        
        if limit is not None:
            records = records[:limit]
        
        return records
    
    async def clear(self, session_id: str) -> None:
        """Clear memory for a session."""
        if session_id in self.storage:
            del self.storage[session_id]
    
    async def get_sessions(self) -> List[str]:
        """Get all session IDs."""
        return list(self.storage.keys())
    
    async def close(self) -> None:
        """No-op for in-memory backend."""
        pass


class RedisBackend(MemoryBackend):
    """Redis backend for production use."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        key_prefix: str = "agentz:memory:",
        ttl: Optional[int] = None
    ):
        """
        Initialize Redis backend.
        
        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for Redis keys
            ttl: TTL for records in seconds (None for no expiration)
        """
        if not REDIS_AVAILABLE:
            raise MemoryError(
                "Redis backend requires 'redis' package. Install with: pip install redis",
                error_code="REDIS_NOT_AVAILABLE"
            )
        
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.ttl = ttl
        self.client: Optional[redis.Redis] = None
    
    async def _ensure_connected(self) -> None:
        """Ensure Redis connection is established."""
        if self.client is None:
            try:
                self.client = redis.from_url(self.redis_url)
                # Test connection
                await self.client.ping()
            except Exception as e:
                raise MemoryConnectionError(
                    backend="redis",
                    connection_string=self.redis_url,
                    original_error=e
                )
    
    def _get_key(self, session_id: str) -> str:
        """Get Redis key for a session."""
        return f"{self.key_prefix}{session_id}"
    
    async def store(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a memory record in Redis."""
        await self._ensure_connected()
        
        record = MemoryRecord(
            session_id=session_id,
            timestamp=time.time(),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        key = self._get_key(session_id)
        record_json = json.dumps(record.to_dict())
        
        try:
            # Add to list
            await self.client.lpush(key, record_json)
            
            # Set TTL if specified
            if self.ttl:
                await self.client.expire(key, self.ttl)
                
        except Exception as e:
            raise MemoryError(
                f"Failed to store memory record: {str(e)}",
                backend="redis",
                error_code="STORE_FAILED"
            )
    
    async def retrieve(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """Retrieve memory records from Redis."""
        await self._ensure_connected()
        
        key = self._get_key(session_id)
        
        try:
            # Calculate range
            start = offset
            end = -1 if limit is None else offset + limit - 1
            
            # Get records (most recent first due to lpush)
            records_json = await self.client.lrange(key, start, end)
            
            # Parse and reverse to get chronological order
            records = []
            for record_json in reversed(records_json):
                record_data = json.loads(record_json)
                records.append(MemoryRecord.from_dict(record_data))
            
            return records
            
        except Exception as e:
            raise MemoryError(
                f"Failed to retrieve memory records: {str(e)}",
                backend="redis",
                error_code="RETRIEVE_FAILED"
            )
    
    async def clear(self, session_id: str) -> None:
        """Clear memory for a session."""
        await self._ensure_connected()
        
        key = self._get_key(session_id)
        
        try:
            await self.client.delete(key)
        except Exception as e:
            raise MemoryError(
                f"Failed to clear memory: {str(e)}",
                backend="redis",
                error_code="CLEAR_FAILED"
            )
    
    async def get_sessions(self) -> List[str]:
        """Get all session IDs."""
        await self._ensure_connected()
        
        try:
            pattern = f"{self.key_prefix}*"
            keys = await self.client.keys(pattern)
            
            # Extract session IDs from keys
            sessions = []
            prefix_len = len(self.key_prefix)
            for key in keys:
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                sessions.append(key[prefix_len:])
            
            return sessions
            
        except Exception as e:
            raise MemoryError(
                f"Failed to get sessions: {str(e)}",
                backend="redis",
                error_code="GET_SESSIONS_FAILED"
            )
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.client = None


class SQLiteBackend(MemoryBackend):
    """SQLite backend for local persistence."""
    
    def __init__(self, db_path: str = "agentz_memory.db"):
        """
        Initialize SQLite backend.
        
        Args:
            db_path: Path to SQLite database file
        """
        if not SQLITE_AVAILABLE:
            raise MemoryError(
                "SQLite backend requires 'aiosqlite' package. Install with: pip install aiosqlite",
                error_code="SQLITE_NOT_AVAILABLE"
            )
        
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
    
    async def _ensure_connected(self) -> None:
        """Ensure database connection and table creation."""
        if self.db is None:
            try:
                self.db = await aiosqlite.connect(self.db_path)
                
                # Create table if not exists
                await self.db.execute("""
                    CREATE TABLE IF NOT EXISTS memory_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT,
                        INDEX(session_id, timestamp)
                    )
                """)
                
                await self.db.commit()
                
            except Exception as e:
                raise MemoryConnectionError(
                    backend="sqlite",
                    connection_string=self.db_path,
                    original_error=e
                )
    
    async def store(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a memory record in SQLite."""
        await self._ensure_connected()
        
        try:
            metadata_json = json.dumps(metadata or {})
            
            await self.db.execute("""
                INSERT INTO memory_records 
                (session_id, timestamp, role, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, time.time(), role, content, metadata_json))
            
            await self.db.commit()
            
        except Exception as e:
            raise MemoryError(
                f"Failed to store memory record: {str(e)}",
                backend="sqlite",
                error_code="STORE_FAILED"
            )
    
    async def retrieve(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[MemoryRecord]:
        """Retrieve memory records from SQLite."""
        await self._ensure_connected()
        
        try:
            query = """
                SELECT session_id, timestamp, role, content, metadata
                FROM memory_records
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """
            
            params = [session_id]
            
            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            elif offset > 0:
                query += " OFFSET ?"
                params.append(offset)
            
            cursor = await self.db.execute(query, params)
            rows = await cursor.fetchall()
            
            records = []
            for row in rows:
                session_id, timestamp, role, content, metadata_json = row
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                record = MemoryRecord(
                    session_id=session_id,
                    timestamp=timestamp,
                    role=role,
                    content=content,
                    metadata=metadata
                )
                records.append(record)
            
            return records
            
        except Exception as e:
            raise MemoryError(
                f"Failed to retrieve memory records: {str(e)}",
                backend="sqlite",
                error_code="RETRIEVE_FAILED"
            )
    
    async def clear(self, session_id: str) -> None:
        """Clear memory for a session."""
        await self._ensure_connected()
        
        try:
            await self.db.execute(
                "DELETE FROM memory_records WHERE session_id = ?",
                (session_id,)
            )
            await self.db.commit()
            
        except Exception as e:
            raise MemoryError(
                f"Failed to clear memory: {str(e)}",
                backend="sqlite",
                error_code="CLEAR_FAILED"
            )
    
    async def get_sessions(self) -> List[str]:
        """Get all session IDs."""
        await self._ensure_connected()
        
        try:
            cursor = await self.db.execute(
                "SELECT DISTINCT session_id FROM memory_records"
            )
            rows = await cursor.fetchall()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            raise MemoryError(
                f"Failed to get sessions: {str(e)}",
                backend="sqlite",
                error_code="GET_SESSIONS_FAILED"
            )
    
    async def close(self) -> None:
        """Close database connection."""
        if self.db:
            await self.db.close()
            self.db = None