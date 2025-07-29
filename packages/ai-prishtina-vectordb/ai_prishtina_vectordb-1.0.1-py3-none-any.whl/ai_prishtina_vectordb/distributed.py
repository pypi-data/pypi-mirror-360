"""
Distributed deployment support for AI Prishtina VectorDB.

This module provides comprehensive distributed computing capabilities including
cluster management, load balancing, data sharding, and fault tolerance.
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import socket
from pathlib import Path

from .logger import AIPrishtinaLogger
from .metrics import AdvancedMetricsCollector
from .exceptions import AIPrishtinaError


class NodeStatus(Enum):
    """Node status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class ShardingStrategy(Enum):
    """Data sharding strategies."""
    HASH_BASED = "hash_based"
    RANGE_BASED = "range_based"
    CONSISTENT_HASH = "consistent_hash"
    CUSTOM = "custom"


@dataclass
class NodeInfo:
    """Information about a cluster node."""
    node_id: str
    host: str
    port: int
    status: NodeStatus = NodeStatus.HEALTHY
    load: float = 0.0
    capacity: int = 1000
    last_heartbeat: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def address(self) -> str:
        """Get node address."""
        return f"{self.host}:{self.port}"
    
    def is_healthy(self) -> bool:
        """Check if node is healthy."""
        return (
            self.status == NodeStatus.HEALTHY and
            time.time() - self.last_heartbeat < 30.0  # 30 seconds timeout
        )


@dataclass
class DistributedConfig:
    """Configuration for distributed deployment."""
    cluster_name: str = "ai_prishtina_cluster"
    node_id: Optional[str] = None
    host: str = "localhost"
    port: int = 8000
    discovery_port: int = 8001
    heartbeat_interval: float = 10.0
    replication_factor: int = 2
    sharding_strategy: ShardingStrategy = ShardingStrategy.CONSISTENT_HASH
    auto_scaling: bool = True
    max_nodes: int = 10
    min_nodes: int = 1
    load_threshold: float = 0.8
    enable_ssl: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None


class ConsistentHashRing:
    """Consistent hashing implementation for data distribution."""
    
    def __init__(self, nodes: List[NodeInfo], replicas: int = 100):
        """Initialize consistent hash ring."""
        self.nodes = {}
        self.ring = {}
        self.replicas = replicas
        self._build_ring(nodes)
    
    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def _build_ring(self, nodes: List[NodeInfo]):
        """Build the hash ring."""
        self.ring.clear()
        self.nodes.clear()
        
        for node in nodes:
            if node.is_healthy():
                self.nodes[node.node_id] = node
                for i in range(self.replicas):
                    key = f"{node.node_id}:{i}"
                    hash_value = self._hash(key)
                    self.ring[hash_value] = node.node_id
    
    def get_node(self, key: str) -> Optional[NodeInfo]:
        """Get the node responsible for a key."""
        if not self.ring:
            return None
        
        hash_value = self._hash(key)
        
        # Find the first node clockwise
        for ring_key in sorted(self.ring.keys()):
            if hash_value <= ring_key:
                node_id = self.ring[ring_key]
                return self.nodes.get(node_id)
        
        # Wrap around to the first node
        first_key = min(self.ring.keys())
        node_id = self.ring[first_key]
        return self.nodes.get(node_id)
    
    def get_nodes(self, key: str, count: int) -> List[NodeInfo]:
        """Get multiple nodes for replication."""
        if not self.ring or count <= 0:
            return []
        
        hash_value = self._hash(key)
        nodes = []
        seen_nodes = set()
        
        sorted_keys = sorted(self.ring.keys())
        start_idx = 0
        
        # Find starting position
        for i, ring_key in enumerate(sorted_keys):
            if hash_value <= ring_key:
                start_idx = i
                break
        
        # Collect nodes
        for i in range(len(sorted_keys)):
            idx = (start_idx + i) % len(sorted_keys)
            ring_key = sorted_keys[idx]
            node_id = self.ring[ring_key]
            
            if node_id not in seen_nodes:
                node = self.nodes.get(node_id)
                if node and node.is_healthy():
                    nodes.append(node)
                    seen_nodes.add(node_id)
                    
                    if len(nodes) >= count:
                        break
        
        return nodes


class LoadBalancer:
    """Load balancer for distributing requests across nodes."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize load balancer."""
        self.logger = logger or AIPrishtinaLogger(name="load_balancer")
        self.nodes: List[NodeInfo] = []
        self.current_index = 0
    
    def add_node(self, node: NodeInfo):
        """Add a node to the load balancer."""
        if node not in self.nodes:
            self.nodes.append(node)
    
    def remove_node(self, node_id: str):
        """Remove a node from the load balancer."""
        self.nodes = [n for n in self.nodes if n.node_id != node_id]
    
    def get_healthy_nodes(self) -> List[NodeInfo]:
        """Get list of healthy nodes."""
        return [node for node in self.nodes if node.is_healthy()]
    
    def select_node_round_robin(self) -> Optional[NodeInfo]:
        """Select node using round-robin algorithm."""
        healthy_nodes = self.get_healthy_nodes()
        if not healthy_nodes:
            return None
        
        node = healthy_nodes[self.current_index % len(healthy_nodes)]
        self.current_index += 1
        return node
    
    def select_node_least_loaded(self) -> Optional[NodeInfo]:
        """Select node with least load."""
        healthy_nodes = self.get_healthy_nodes()
        if not healthy_nodes:
            return None
        
        return min(healthy_nodes, key=lambda n: n.load)
    
    def select_node_weighted(self) -> Optional[NodeInfo]:
        """Select node using weighted selection based on capacity."""
        healthy_nodes = self.get_healthy_nodes()
        if not healthy_nodes:
            return None
        
        # Calculate weights based on available capacity
        total_weight = sum(max(1, node.capacity - node.load) for node in healthy_nodes)
        if total_weight == 0:
            return healthy_nodes[0]
        
        import random
        target = random.uniform(0, total_weight)
        current = 0
        
        for node in healthy_nodes:
            weight = max(1, node.capacity - node.load)
            current += weight
            if current >= target:
                return node
        
        return healthy_nodes[-1]


class ClusterManager:
    """Manages a distributed cluster of vector database nodes."""
    
    def __init__(
        self,
        config: DistributedConfig,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[AdvancedMetricsCollector] = None
    ):
        """Initialize cluster manager."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="cluster_manager")
        self.metrics = metrics or AdvancedMetricsCollector(logger)
        
        # Generate node ID if not provided
        if not self.config.node_id:
            self.config.node_id = f"node_{socket.gethostname()}_{self.config.port}"
        
        # Cluster state
        self.nodes: Dict[str, NodeInfo] = {}
        self.local_node = NodeInfo(
            node_id=self.config.node_id,
            host=self.config.host,
            port=self.config.port
        )
        self.nodes[self.config.node_id] = self.local_node
        
        # Components
        self.hash_ring = ConsistentHashRing(list(self.nodes.values()))
        self.load_balancer = LoadBalancer(logger)
        
        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.discovery_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        
        # HTTP session for inter-node communication
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """Start the cluster manager."""
        await self.logger.info(f"Starting cluster manager for node {self.config.node_id}")
        
        # Initialize HTTP session
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        self.session = aiohttp.ClientSession(connector=connector)
        
        # Start background tasks
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.discovery_task = asyncio.create_task(self._discovery_loop())
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        await self.logger.info("Cluster manager started successfully")
    
    async def stop(self):
        """Stop the cluster manager."""
        await self.logger.info("Stopping cluster manager")
        
        # Cancel background tasks
        for task in [self.heartbeat_task, self.discovery_task, self.health_check_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        await self.logger.info("Cluster manager stopped")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to other nodes."""
        while True:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(self.config.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Heartbeat error: {str(e)}")
                await asyncio.sleep(self.config.heartbeat_interval)
    
    async def _discovery_loop(self):
        """Discover other nodes in the cluster."""
        while True:
            try:
                await self._discover_nodes()
                await asyncio.sleep(30.0)  # Discovery every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Discovery error: {str(e)}")
                await asyncio.sleep(30.0)
    
    async def _health_check_loop(self):
        """Check health of all nodes."""
        while True:
            try:
                await self._check_node_health()
                await asyncio.sleep(15.0)  # Health check every 15 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Health check error: {str(e)}")
                await asyncio.sleep(15.0)
    
    async def _send_heartbeat(self):
        """Send heartbeat to all known nodes."""
        if not self.session:
            return
        
        heartbeat_data = {
            "node_id": self.local_node.node_id,
            "host": self.local_node.host,
            "port": self.local_node.port,
            "status": self.local_node.status.value,
            "load": self.local_node.load,
            "capacity": self.local_node.capacity,
            "timestamp": time.time()
        }
        
        for node_id, node in self.nodes.items():
            if node_id != self.config.node_id and node.is_healthy():
                try:
                    url = f"http://{node.address}/heartbeat"
                    async with self.session.post(url, json=heartbeat_data, timeout=5.0) as response:
                        if response.status == 200:
                            await self.logger.debug(f"Heartbeat sent to {node_id}")
                except Exception as e:
                    await self.logger.warning(f"Failed to send heartbeat to {node_id}: {str(e)}")
    
    async def _discover_nodes(self):
        """Discover new nodes in the cluster."""
        # This is a simplified discovery mechanism
        # In production, you might use service discovery tools like Consul, etcd, etc.
        pass
    
    async def _check_node_health(self):
        """Check health of all nodes."""
        current_time = time.time()
        unhealthy_nodes = []
        
        for node_id, node in self.nodes.items():
            if node_id != self.config.node_id:
                if current_time - node.last_heartbeat > 30.0:
                    node.status = NodeStatus.OFFLINE
                    unhealthy_nodes.append(node_id)
        
        # Remove unhealthy nodes and rebuild hash ring
        if unhealthy_nodes:
            for node_id in unhealthy_nodes:
                await self.logger.warning(f"Node {node_id} marked as offline")
                self.load_balancer.remove_node(node_id)
            
            healthy_nodes = [node for node in self.nodes.values() if node.is_healthy()]
            self.hash_ring = ConsistentHashRing(healthy_nodes)
    
    def get_node_for_key(self, key: str) -> Optional[NodeInfo]:
        """Get the node responsible for a specific key."""
        return self.hash_ring.get_node(key)
    
    def get_nodes_for_replication(self, key: str) -> List[NodeInfo]:
        """Get nodes for data replication."""
        return self.hash_ring.get_nodes(key, self.config.replication_factor)
    
    async def add_node(self, node_info: NodeInfo):
        """Add a new node to the cluster."""
        self.nodes[node_info.node_id] = node_info
        self.load_balancer.add_node(node_info)
        
        # Rebuild hash ring
        healthy_nodes = [node for node in self.nodes.values() if node.is_healthy()]
        self.hash_ring = ConsistentHashRing(healthy_nodes)
        
        await self.logger.info(f"Added node {node_info.node_id} to cluster")
    
    async def remove_node(self, node_id: str):
        """Remove a node from the cluster."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.load_balancer.remove_node(node_id)
            
            # Rebuild hash ring
            healthy_nodes = [node for node in self.nodes.values() if node.is_healthy()]
            self.hash_ring = ConsistentHashRing(healthy_nodes)
            
            await self.logger.info(f"Removed node {node_id} from cluster")
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status."""
        healthy_nodes = [node for node in self.nodes.values() if node.is_healthy()]
        total_capacity = sum(node.capacity for node in healthy_nodes)
        total_load = sum(node.load for node in healthy_nodes)
        
        return {
            "cluster_name": self.config.cluster_name,
            "total_nodes": len(self.nodes),
            "healthy_nodes": len(healthy_nodes),
            "total_capacity": total_capacity,
            "total_load": total_load,
            "load_percentage": (total_load / total_capacity * 100) if total_capacity > 0 else 0,
            "nodes": {
                node_id: {
                    "status": node.status.value,
                    "load": node.load,
                    "capacity": node.capacity,
                    "address": node.address,
                    "last_heartbeat": node.last_heartbeat
                }
                for node_id, node in self.nodes.items()
            }
        }


class DistributedError(AIPrishtinaError):
    """Exception raised for distributed system errors."""
    pass
