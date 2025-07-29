"""
Real-time collaboration features for AI Prishtina VectorDB.

This module provides real-time collaboration capabilities including
live updates, conflict resolution, version control, and team management.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
try:
    import websockets
except ImportError:
    websockets = None
from datetime import datetime, timezone

from .logger import AIPrishtinaLogger
from .metrics import AdvancedMetricsCollector
from .exceptions import AIPrishtinaError


class EventType(Enum):
    """Collaboration event types."""
    DOCUMENT_ADDED = "document_added"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_DELETED = "document_deleted"
    COLLECTION_CREATED = "collection_created"
    COLLECTION_UPDATED = "collection_updated"
    COLLECTION_DELETED = "collection_deleted"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    QUERY_EXECUTED = "query_executed"
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    MANUAL = "manual"
    VERSION_BRANCH = "version_branch"


class UserRole(Enum):
    """User roles for collaboration."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"


@dataclass
class User:
    """Represents a collaboration user."""
    user_id: str
    username: str
    email: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationEvent:
    """Represents a collaboration event."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.DOCUMENT_UPDATED
    user_id: str = ""
    collection_name: str = ""
    document_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "user_id": self.user_id,
            "collection_name": self.collection_name,
            "document_id": self.document_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollaborationEvent':
        """Create event from dictionary."""
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            event_type=EventType(data["event_type"]),
            user_id=data["user_id"],
            collection_name=data["collection_name"],
            document_id=data.get("document_id"),
            data=data.get("data", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data.get("version", 1)
        )


@dataclass
class Conflict:
    """Represents a data conflict."""
    conflict_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    collection_name: str = ""
    document_id: str = ""
    conflicting_events: List[CollaborationEvent] = field(default_factory=list)
    resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LAST_WRITE_WINS
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_data: Optional[Dict[str, Any]] = None


class WebSocketManager:
    """Manages WebSocket connections for real-time collaboration."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize WebSocket manager."""
        self.logger = logger or AIPrishtinaLogger(name="websocket_manager")
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.collection_subscribers: Dict[str, Set[str]] = {}  # collection -> user_ids
    
    async def add_connection(self, connection_id: str, websocket: websockets.WebSocketServerProtocol):
        """Add a new WebSocket connection."""
        self.connections[connection_id] = websocket
        await self.logger.debug(f"Added WebSocket connection: {connection_id}")
    
    async def remove_connection(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]
            
            # Remove from user connections
            for user_id, conn_ids in self.user_connections.items():
                conn_ids.discard(connection_id)
            
            await self.logger.debug(f"Removed WebSocket connection: {connection_id}")
    
    async def associate_user(self, connection_id: str, user_id: str):
        """Associate a connection with a user."""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
    
    async def subscribe_to_collection(self, user_id: str, collection_name: str):
        """Subscribe user to collection updates."""
        if collection_name not in self.collection_subscribers:
            self.collection_subscribers[collection_name] = set()
        self.collection_subscribers[collection_name].add(user_id)
        await self.logger.debug(f"User {user_id} subscribed to collection {collection_name}")
    
    async def unsubscribe_from_collection(self, user_id: str, collection_name: str):
        """Unsubscribe user from collection updates."""
        if collection_name in self.collection_subscribers:
            self.collection_subscribers[collection_name].discard(user_id)
    
    async def broadcast_to_collection(self, collection_name: str, event: CollaborationEvent):
        """Broadcast event to all subscribers of a collection."""
        if collection_name not in self.collection_subscribers:
            return
        
        subscribers = self.collection_subscribers[collection_name]
        message = json.dumps(event.to_dict())
        
        for user_id in subscribers:
            await self.send_to_user(user_id, message)
    
    async def send_to_user(self, user_id: str, message: str):
        """Send message to all connections of a user."""
        if user_id not in self.user_connections:
            return
        
        connection_ids = list(self.user_connections[user_id])
        for connection_id in connection_ids:
            if connection_id in self.connections:
                try:
                    websocket = self.connections[connection_id]
                    await websocket.send(message)
                except Exception as e:
                    await self.logger.warning(f"Failed to send message to {connection_id}: {str(e)}")
                    await self.remove_connection(connection_id)


class ConflictResolver:
    """Handles conflict detection and resolution."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize conflict resolver."""
        self.logger = logger or AIPrishtinaLogger(name="conflict_resolver")
        self.active_conflicts: Dict[str, Conflict] = {}
    
    async def detect_conflict(self, events: List[CollaborationEvent]) -> Optional[Conflict]:
        """Detect conflicts between events."""
        if len(events) < 2:
            return None
        
        # Group events by document
        document_events = {}
        for event in events:
            if event.document_id:
                key = f"{event.collection_name}:{event.document_id}"
                if key not in document_events:
                    document_events[key] = []
                document_events[key].append(event)
        
        # Check for conflicts
        for key, doc_events in document_events.items():
            if len(doc_events) > 1:
                # Sort by timestamp
                doc_events.sort(key=lambda e: e.timestamp)
                
                # Check for overlapping modifications
                for i in range(len(doc_events) - 1):
                    event1 = doc_events[i]
                    event2 = doc_events[i + 1]
                    
                    # If events are close in time and from different users
                    time_diff = (event2.timestamp - event1.timestamp).total_seconds()
                    if time_diff < 5.0 and event1.user_id != event2.user_id:
                        conflict = Conflict(
                            collection_name=event1.collection_name,
                            document_id=event1.document_id,
                            conflicting_events=[event1, event2]
                        )
                        
                        self.active_conflicts[conflict.conflict_id] = conflict
                        await self.logger.warning(f"Conflict detected: {conflict.conflict_id}")
                        return conflict
        
        return None
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        strategy: ConflictResolutionStrategy,
        resolver_user_id: str,
        resolution_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Resolve a conflict using the specified strategy."""
        if conflict_id not in self.active_conflicts:
            return False
        
        conflict = self.active_conflicts[conflict_id]
        
        try:
            if strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
                # Use the event with the latest timestamp
                latest_event = max(conflict.conflicting_events, key=lambda e: e.timestamp)
                conflict.resolution_data = latest_event.data
            
            elif strategy == ConflictResolutionStrategy.FIRST_WRITE_WINS:
                # Use the event with the earliest timestamp
                earliest_event = min(conflict.conflicting_events, key=lambda e: e.timestamp)
                conflict.resolution_data = earliest_event.data
            
            elif strategy == ConflictResolutionStrategy.MERGE:
                # Attempt to merge the conflicting data
                merged_data = self._merge_data([e.data for e in conflict.conflicting_events])
                conflict.resolution_data = merged_data
            
            elif strategy == ConflictResolutionStrategy.MANUAL:
                # Use manually provided resolution data
                conflict.resolution_data = resolution_data
            
            conflict.resolved = True
            conflict.resolved_by = resolver_user_id
            conflict.resolved_at = datetime.now(timezone.utc)
            conflict.resolution_strategy = strategy
            
            await self.logger.info(f"Conflict {conflict_id} resolved using {strategy.value}")
            return True
            
        except Exception as e:
            await self.logger.error(f"Failed to resolve conflict {conflict_id}: {str(e)}")
            return False
    
    def _merge_data(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge conflicting data (simplified implementation)."""
        if not data_list:
            return {}
        
        merged = data_list[0].copy()
        
        for data in data_list[1:]:
            for key, value in data.items():
                if key not in merged:
                    merged[key] = value
                elif isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key].update(value)
                elif isinstance(merged[key], list) and isinstance(value, list):
                    merged[key].extend(value)
                else:
                    # For conflicting values, keep the latest one
                    merged[key] = value
        
        return merged


class VersionControl:
    """Handles versioning for collaborative editing."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize version control."""
        self.logger = logger or AIPrishtinaLogger(name="version_control")
        self.versions: Dict[str, List[CollaborationEvent]] = {}  # document_id -> versions
    
    async def create_version(self, event: CollaborationEvent) -> int:
        """Create a new version for a document."""
        if not event.document_id:
            return 1
        
        if event.document_id not in self.versions:
            self.versions[event.document_id] = []
        
        # Assign version number
        event.version = len(self.versions[event.document_id]) + 1
        self.versions[event.document_id].append(event)
        
        await self.logger.debug(f"Created version {event.version} for document {event.document_id}")
        return event.version
    
    async def get_version(self, document_id: str, version: int) -> Optional[CollaborationEvent]:
        """Get a specific version of a document."""
        if document_id not in self.versions:
            return None
        
        versions = self.versions[document_id]
        if 1 <= version <= len(versions):
            return versions[version - 1]
        
        return None
    
    async def get_version_history(self, document_id: str) -> List[CollaborationEvent]:
        """Get version history for a document."""
        return self.versions.get(document_id, [])
    
    async def revert_to_version(self, document_id: str, version: int, user_id: str) -> Optional[CollaborationEvent]:
        """Revert document to a specific version."""
        target_version = await self.get_version(document_id, version)
        if not target_version:
            return None
        
        # Create a new event based on the target version
        revert_event = CollaborationEvent(
            event_type=EventType.DOCUMENT_UPDATED,
            user_id=user_id,
            collection_name=target_version.collection_name,
            document_id=document_id,
            data=target_version.data.copy()
        )
        
        # Add to version history
        await self.create_version(revert_event)
        
        await self.logger.info(f"Reverted document {document_id} to version {version}")
        return revert_event


class CollaborationManager:
    """Main collaboration manager coordinating all collaboration features."""
    
    def __init__(
        self,
        database,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[AdvancedMetricsCollector] = None
    ):
        """Initialize collaboration manager."""
        self.database = database
        self.logger = logger or AIPrishtinaLogger(name="collaboration_manager")
        self.metrics = metrics or AdvancedMetricsCollector(logger)
        
        # Components
        self.websocket_manager = WebSocketManager(logger)
        self.conflict_resolver = ConflictResolver(logger)
        self.version_control = VersionControl(logger)
        
        # State
        self.users: Dict[str, User] = {}
        self.event_history: List[CollaborationEvent] = []
        self.event_callbacks: List[Callable[[CollaborationEvent], None]] = []
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the collaboration manager."""
        await self.logger.info("Starting collaboration manager")
        
        # Start background cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        await self.logger.info("Collaboration manager started")
    
    async def stop(self):
        """Stop the collaboration manager."""
        await self.logger.info("Stopping collaboration manager")
        
        # Cancel cleanup task
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        await self.logger.info("Collaboration manager stopped")
    
    async def add_user(self, user: User):
        """Add a user to the collaboration session."""
        self.users[user.user_id] = user
        
        # Create user joined event
        event = CollaborationEvent(
            event_type=EventType.USER_JOINED,
            user_id=user.user_id,
            data={"username": user.username, "role": user.role.value}
        )
        
        await self._process_event(event)
        await self.logger.info(f"User {user.username} joined collaboration")
    
    async def remove_user(self, user_id: str):
        """Remove a user from the collaboration session."""
        if user_id in self.users:
            user = self.users[user_id]
            del self.users[user_id]
            
            # Create user left event
            event = CollaborationEvent(
                event_type=EventType.USER_LEFT,
                user_id=user_id,
                data={"username": user.username}
            )
            
            await self._process_event(event)
            await self.logger.info(f"User {user.username} left collaboration")
    
    async def handle_document_change(
        self,
        user_id: str,
        collection_name: str,
        document_id: str,
        change_type: EventType,
        data: Dict[str, Any]
    ):
        """Handle a document change event."""
        event = CollaborationEvent(
            event_type=change_type,
            user_id=user_id,
            collection_name=collection_name,
            document_id=document_id,
            data=data
        )
        
        # Create version
        await self.version_control.create_version(event)
        
        # Check for conflicts
        recent_events = [e for e in self.event_history[-10:] if e.document_id == document_id]
        recent_events.append(event)
        
        conflict = await self.conflict_resolver.detect_conflict(recent_events)
        if conflict:
            # Notify about conflict
            conflict_event = CollaborationEvent(
                event_type=EventType.CONFLICT_DETECTED,
                user_id="system",
                collection_name=collection_name,
                document_id=document_id,
                data={"conflict_id": conflict.conflict_id}
            )
            await self._process_event(conflict_event)
        
        await self._process_event(event)
    
    async def _process_event(self, event: CollaborationEvent):
        """Process a collaboration event."""
        # Add to history
        self.event_history.append(event)
        
        # Record metrics
        await self.metrics.record_metric(f"collaboration.{event.event_type.value}", 1)
        
        # Broadcast to subscribers
        await self.websocket_manager.broadcast_to_collection(event.collection_name, event)
        
        # Call event callbacks
        for callback in self.event_callbacks:
            try:
                await callback(event)
            except Exception as e:
                await self.logger.error(f"Event callback error: {str(e)}")
        
        await self.logger.debug(f"Processed event: {event.event_type.value}")
    
    def add_event_callback(self, callback: Callable[[CollaborationEvent], None]):
        """Add an event callback."""
        self.event_callbacks.append(callback)
    
    async def _cleanup_loop(self):
        """Background cleanup task."""
        while True:
            try:
                # Clean up old events (keep last 1000)
                if len(self.event_history) > 1000:
                    self.event_history = self.event_history[-1000:]
                
                # Update user last seen times
                current_time = datetime.now(timezone.utc)
                for user in self.users.values():
                    if user.is_active:
                        user.last_seen = current_time
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Cleanup error: {str(e)}")
                await asyncio.sleep(300)


class CollaborationError(AIPrishtinaError):
    """Exception raised for collaboration errors."""
    pass
