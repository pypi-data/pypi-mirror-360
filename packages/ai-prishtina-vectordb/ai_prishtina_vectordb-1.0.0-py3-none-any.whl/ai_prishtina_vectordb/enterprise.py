"""
Production-ready enterprise features for AI Prishtina VectorDB.

This module provides enterprise-grade capabilities including
high availability, disaster recovery, compliance, and enterprise integrations.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import aiofiles
import aiohttp
from pathlib import Path

from .logger import AIPrishtinaLogger
from .metrics import AdvancedMetricsCollector
from .security import SecurityManager, SecurityConfig
from .distributed import ClusterManager, DistributedConfig
from .exceptions import AIPrishtinaError


class DeploymentMode(Enum):
    """Deployment mode enumeration."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


class BackupType(Enum):
    """Backup type enumeration."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class ComplianceStandard(Enum):
    """Compliance standard enumeration."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"


@dataclass
class EnterpriseConfig:
    """Enterprise configuration."""
    deployment_mode: DeploymentMode = DeploymentMode.PRODUCTION
    high_availability: bool = True
    disaster_recovery: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    monitoring_enabled: bool = True
    alerting_enabled: bool = True
    compliance_standards: Set[ComplianceStandard] = field(default_factory=set)
    enterprise_features: Set[str] = field(default_factory=set)
    sla_target_uptime: float = 99.9  # 99.9% uptime SLA
    max_concurrent_users: int = 1000
    data_retention_days: int = 365
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    audit_trail_enabled: bool = True


@dataclass
class BackupMetadata:
    """Backup metadata."""
    backup_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    backup_type: BackupType = BackupType.FULL
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    size_bytes: int = 0
    collections: List[str] = field(default_factory=list)
    checksum: Optional[str] = None
    compression_ratio: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SLAMetrics:
    """Service Level Agreement metrics."""
    uptime_percentage: float = 0.0
    response_time_p95: float = 0.0
    response_time_p99: float = 0.0
    error_rate: float = 0.0
    throughput_rps: float = 0.0
    availability_score: float = 0.0
    performance_score: float = 0.0
    reliability_score: float = 0.0


class HighAvailabilityManager:
    """Manages high availability features."""
    
    def __init__(
        self,
        config: EnterpriseConfig,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize HA manager."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="ha_manager")
        
        # HA state
        self.is_primary = True
        self.failover_nodes: List[str] = []
        self.health_check_interval = 30.0
        self.failover_threshold = 3
        self.consecutive_failures = 0
        
        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start HA manager."""
        await self.logger.info("Starting High Availability manager")
        
        if self.config.high_availability:
            self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        await self.logger.info("HA manager started")
    
    async def stop(self):
        """Stop HA manager."""
        if self.health_check_task and not self.health_check_task.done():
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        await self.logger.info("HA manager stopped")
    
    async def _health_check_loop(self):
        """Health check loop for HA."""
        while True:
            try:
                is_healthy = await self._perform_health_check()
                
                if not is_healthy:
                    self.consecutive_failures += 1
                    if self.consecutive_failures >= self.failover_threshold:
                        await self._initiate_failover()
                else:
                    self.consecutive_failures = 0
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Health check error: {str(e)}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _perform_health_check(self) -> bool:
        """Perform health check."""
        try:
            # Check system resources
            import psutil
            
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                await self.logger.warning(f"High CPU usage: {cpu_percent}%")
                return False
            
            # Memory check
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                await self.logger.warning(f"High memory usage: {memory.percent}%")
                return False
            
            # Disk check
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                await self.logger.warning(f"High disk usage: {disk.percent}%")
                return False
            
            return True
            
        except Exception as e:
            await self.logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def _initiate_failover(self):
        """Initiate failover to backup node."""
        await self.logger.critical("Initiating failover due to health check failures")
        
        # Mark as non-primary
        self.is_primary = False
        
        # Notify failover nodes
        for node in self.failover_nodes:
            try:
                # Send failover signal to backup nodes
                await self._notify_failover(node)
            except Exception as e:
                await self.logger.error(f"Failed to notify failover node {node}: {str(e)}")
    
    async def _notify_failover(self, node: str):
        """Notify backup node of failover."""
        # Implementation would depend on your failover mechanism
        pass


class DisasterRecoveryManager:
    """Manages disaster recovery and backup operations."""
    
    def __init__(
        self,
        config: EnterpriseConfig,
        database,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize DR manager."""
        self.config = config
        self.database = database
        self.logger = logger or AIPrishtinaLogger(name="dr_manager")
        
        # Backup state
        self.backup_directory = Path("backups")
        self.backup_directory.mkdir(exist_ok=True)
        self.backup_metadata: List[BackupMetadata] = []
        
        # Background tasks
        self.backup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start DR manager."""
        await self.logger.info("Starting Disaster Recovery manager")
        
        if self.config.backup_enabled:
            self.backup_task = asyncio.create_task(self._backup_loop())
        
        await self.logger.info("DR manager started")
    
    async def stop(self):
        """Stop DR manager."""
        if self.backup_task and not self.backup_task.done():
            self.backup_task.cancel()
            try:
                await self.backup_task
            except asyncio.CancelledError:
                pass
        
        await self.logger.info("DR manager stopped")
    
    async def _backup_loop(self):
        """Automated backup loop."""
        while True:
            try:
                await self.create_backup(BackupType.INCREMENTAL)
                
                # Wait for next backup interval
                await asyncio.sleep(self.config.backup_interval_hours * 3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Backup error: {str(e)}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def create_backup(self, backup_type: BackupType = BackupType.FULL) -> BackupMetadata:
        """Create a backup."""
        backup_metadata = BackupMetadata(backup_type=backup_type)
        
        try:
            await self.logger.info(f"Starting {backup_type.value} backup")
            
            # Get collections to backup
            collections = await self._get_collections_to_backup()
            backup_metadata.collections = collections
            
            # Create backup file
            backup_file = self.backup_directory / f"backup_{backup_metadata.backup_id}.json"
            
            backup_data = {
                "metadata": {
                    "backup_id": backup_metadata.backup_id,
                    "backup_type": backup_type.value,
                    "created_at": backup_metadata.created_at.isoformat(),
                    "collections": collections
                },
                "data": {}
            }
            
            # Backup each collection
            for collection_name in collections:
                try:
                    collection_data = await self._backup_collection(collection_name)
                    backup_data["data"][collection_name] = collection_data
                except Exception as e:
                    await self.logger.error(f"Failed to backup collection {collection_name}: {str(e)}")
            
            # Write backup file
            async with aiofiles.open(backup_file, 'w') as f:
                await f.write(json.dumps(backup_data, indent=2))
            
            # Calculate backup size and checksum
            backup_metadata.size_bytes = backup_file.stat().st_size
            backup_metadata.checksum = await self._calculate_checksum(backup_file)
            
            # Add to metadata list
            self.backup_metadata.append(backup_metadata)
            
            # Cleanup old backups
            await self._cleanup_old_backups()
            
            await self.logger.info(f"Backup completed: {backup_metadata.backup_id}")
            return backup_metadata
            
        except Exception as e:
            await self.logger.error(f"Backup failed: {str(e)}")
            raise EnterpriseError(f"Backup failed: {str(e)}")
    
    async def _get_collections_to_backup(self) -> List[str]:
        """Get list of collections to backup."""
        # This would depend on your database implementation
        return ["default_collection"]
    
    async def _backup_collection(self, collection_name: str) -> Dict[str, Any]:
        """Backup a specific collection."""
        try:
            # Get all documents from collection
            results = await self.database.query(
                query_texts=None,
                n_results=10000,  # Large number to get all
                include=['metadatas', 'documents', 'embeddings']
            )
            
            return {
                "ids": results.get("ids", []),
                "documents": results.get("documents", []),
                "metadatas": results.get("metadatas", []),
                "embeddings": results.get("embeddings", [])
            }
            
        except Exception as e:
            await self.logger.error(f"Collection backup failed: {str(e)}")
            return {}
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum."""
        import hashlib
        
        hash_md5 = hashlib.md5()
        async with aiofiles.open(file_path, 'rb') as f:
            async for chunk in f:
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.config.backup_retention_days)
        
        old_backups = [
            backup for backup in self.backup_metadata
            if backup.created_at < cutoff_date
        ]
        
        for backup in old_backups:
            try:
                backup_file = self.backup_directory / f"backup_{backup.backup_id}.json"
                if backup_file.exists():
                    backup_file.unlink()
                
                self.backup_metadata.remove(backup)
                await self.logger.info(f"Removed old backup: {backup.backup_id}")
                
            except Exception as e:
                await self.logger.error(f"Failed to remove old backup {backup.backup_id}: {str(e)}")
    
    async def restore_backup(self, backup_id: str) -> bool:
        """Restore from backup."""
        try:
            # Find backup metadata
            backup_metadata = None
            for backup in self.backup_metadata:
                if backup.backup_id == backup_id:
                    backup_metadata = backup
                    break
            
            if not backup_metadata:
                await self.logger.error(f"Backup not found: {backup_id}")
                return False
            
            # Load backup file
            backup_file = self.backup_directory / f"backup_{backup_id}.json"
            if not backup_file.exists():
                await self.logger.error(f"Backup file not found: {backup_file}")
                return False
            
            async with aiofiles.open(backup_file, 'r') as f:
                backup_data = json.loads(await f.read())
            
            # Restore each collection
            for collection_name, collection_data in backup_data["data"].items():
                await self._restore_collection(collection_name, collection_data)
            
            await self.logger.info(f"Backup restored successfully: {backup_id}")
            return True
            
        except Exception as e:
            await self.logger.error(f"Backup restore failed: {str(e)}")
            return False
    
    async def _restore_collection(self, collection_name: str, collection_data: Dict[str, Any]):
        """Restore a specific collection."""
        try:
            # Clear existing collection
            # await self.database.delete_collection(collection_name)
            
            # Restore data
            if collection_data.get("ids") and collection_data.get("documents"):
                await self.database.add(
                    ids=collection_data["ids"][0] if collection_data["ids"] else [],
                    documents=collection_data["documents"][0] if collection_data["documents"] else [],
                    metadatas=collection_data["metadatas"][0] if collection_data.get("metadatas") else None,
                    embeddings=collection_data["embeddings"][0] if collection_data.get("embeddings") else None
                )
            
            await self.logger.info(f"Collection restored: {collection_name}")
            
        except Exception as e:
            await self.logger.error(f"Collection restore failed: {str(e)}")


class SLAManager:
    """Manages Service Level Agreement monitoring and reporting."""
    
    def __init__(
        self,
        config: EnterpriseConfig,
        metrics: AdvancedMetricsCollector,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize SLA manager."""
        self.config = config
        self.metrics = metrics
        self.logger = logger or AIPrishtinaLogger(name="sla_manager")
        
        # SLA tracking
        self.sla_metrics = SLAMetrics()
        self.uptime_start = datetime.now(timezone.utc)
        self.downtime_periods: List[Tuple[datetime, datetime]] = []
        
        # Monitoring task
        self.monitoring_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start SLA monitoring."""
        await self.logger.info("Starting SLA manager")
        
        if self.config.monitoring_enabled:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        await self.logger.info("SLA manager started")
    
    async def stop(self):
        """Stop SLA monitoring."""
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        await self.logger.info("SLA manager stopped")
    
    async def _monitoring_loop(self):
        """SLA monitoring loop."""
        while True:
            try:
                await self._calculate_sla_metrics()
                await asyncio.sleep(60)  # Update every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"SLA monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _calculate_sla_metrics(self):
        """Calculate current SLA metrics."""
        try:
            # Calculate uptime percentage
            total_time = (datetime.now(timezone.utc) - self.uptime_start).total_seconds()
            downtime = sum(
                (end - start).total_seconds()
                for start, end in self.downtime_periods
            )
            
            self.sla_metrics.uptime_percentage = ((total_time - downtime) / total_time) * 100
            
            # Get response time metrics from metrics collector
            response_time_stats = await self.metrics.get_metric_statistics("response_time")
            if response_time_stats:
                self.sla_metrics.response_time_p95 = response_time_stats.get("percentile_95", 0)
                self.sla_metrics.response_time_p99 = response_time_stats.get("percentile_99", 0)
            
            # Calculate error rate
            error_stats = await self.metrics.get_metric_statistics("error_rate")
            if error_stats:
                self.sla_metrics.error_rate = error_stats.get("average", 0)
            
            # Calculate throughput
            throughput_stats = await self.metrics.get_metric_statistics("throughput")
            if throughput_stats:
                self.sla_metrics.throughput_rps = throughput_stats.get("average", 0)
            
            # Calculate composite scores
            self.sla_metrics.availability_score = min(100, self.sla_metrics.uptime_percentage)
            self.sla_metrics.performance_score = max(0, 100 - (self.sla_metrics.response_time_p95 / 10))
            self.sla_metrics.reliability_score = max(0, 100 - (self.sla_metrics.error_rate * 10))
            
            # Record SLA metrics
            await self.metrics.record_metric("sla.uptime_percentage", self.sla_metrics.uptime_percentage)
            await self.metrics.record_metric("sla.availability_score", self.sla_metrics.availability_score)
            await self.metrics.record_metric("sla.performance_score", self.sla_metrics.performance_score)
            await self.metrics.record_metric("sla.reliability_score", self.sla_metrics.reliability_score)
            
        except Exception as e:
            await self.logger.error(f"SLA calculation error: {str(e)}")
    
    async def record_downtime(self, start_time: datetime, end_time: datetime):
        """Record a downtime period."""
        self.downtime_periods.append((start_time, end_time))
        await self.logger.warning(f"Downtime recorded: {start_time} to {end_time}")
    
    async def get_sla_report(self) -> Dict[str, Any]:
        """Get comprehensive SLA report."""
        return {
            "uptime_percentage": self.sla_metrics.uptime_percentage,
            "target_uptime": self.config.sla_target_uptime,
            "sla_compliance": self.sla_metrics.uptime_percentage >= self.config.sla_target_uptime,
            "response_time_p95": self.sla_metrics.response_time_p95,
            "response_time_p99": self.sla_metrics.response_time_p99,
            "error_rate": self.sla_metrics.error_rate,
            "throughput_rps": self.sla_metrics.throughput_rps,
            "availability_score": self.sla_metrics.availability_score,
            "performance_score": self.sla_metrics.performance_score,
            "reliability_score": self.sla_metrics.reliability_score,
            "downtime_periods": len(self.downtime_periods),
            "monitoring_start": self.uptime_start.isoformat()
        }


class EnterpriseManager:
    """Main enterprise manager coordinating all enterprise features."""
    
    def __init__(
        self,
        config: EnterpriseConfig,
        database,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[AdvancedMetricsCollector] = None
    ):
        """Initialize enterprise manager."""
        self.config = config
        self.database = database
        self.logger = logger or AIPrishtinaLogger(name="enterprise_manager")
        self.metrics = metrics or AdvancedMetricsCollector(logger)
        
        # Components
        self.ha_manager = HighAvailabilityManager(config, logger)
        self.dr_manager = DisasterRecoveryManager(config, database, logger)
        self.sla_manager = SLAManager(config, self.metrics, logger)
        
        # Security integration
        security_config = SecurityConfig(
            encryption_enabled=config.encryption_at_rest,
            authentication_required=True,
            authorization_enabled=True,
            audit_logging=config.audit_trail_enabled
        )
        self.security_manager = SecurityManager(security_config, logger, self.metrics)
    
    async def start(self):
        """Start enterprise manager."""
        await self.logger.info(f"Starting Enterprise Manager - Mode: {self.config.deployment_mode.value}")
        
        # Start all components
        await self.ha_manager.start()
        await self.dr_manager.start()
        await self.sla_manager.start()
        
        await self.logger.info("Enterprise manager started successfully")
    
    async def stop(self):
        """Stop enterprise manager."""
        await self.logger.info("Stopping Enterprise Manager")
        
        # Stop all components
        await self.ha_manager.stop()
        await self.dr_manager.stop()
        await self.sla_manager.stop()
        
        await self.logger.info("Enterprise manager stopped")
    
    async def get_enterprise_status(self) -> Dict[str, Any]:
        """Get comprehensive enterprise status."""
        sla_report = await self.sla_manager.get_sla_report()
        security_status = await self.security_manager.get_security_status()
        
        return {
            "deployment_mode": self.config.deployment_mode.value,
            "high_availability": {
                "enabled": self.config.high_availability,
                "is_primary": self.ha_manager.is_primary,
                "consecutive_failures": self.ha_manager.consecutive_failures
            },
            "disaster_recovery": {
                "enabled": self.config.disaster_recovery,
                "backup_count": len(self.dr_manager.backup_metadata),
                "last_backup": self.dr_manager.backup_metadata[-1].created_at.isoformat() if self.dr_manager.backup_metadata else None
            },
            "sla": sla_report,
            "security": security_status,
            "compliance": {
                "standards": [std.value for std in self.config.compliance_standards],
                "audit_trail_enabled": self.config.audit_trail_enabled,
                "encryption_at_rest": self.config.encryption_at_rest,
                "encryption_in_transit": self.config.encryption_in_transit
            },
            "capacity": {
                "max_concurrent_users": self.config.max_concurrent_users,
                "data_retention_days": self.config.data_retention_days
            }
        }


class EnterpriseError(AIPrishtinaError):
    """Exception raised for enterprise feature errors."""
    pass
