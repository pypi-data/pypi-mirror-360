"""
Multi-tenant support for AI Prishtina VectorDB.

This module provides comprehensive multi-tenancy capabilities including
tenant isolation, resource management, billing, and tenant-specific configurations.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta

from .logger import AIPrishtinaLogger
from .metrics import AdvancedMetricsCollector
from .security import SecurityManager, User, PermissionType
from .exceptions import AIPrishtinaError


class TenantTier(Enum):
    """Tenant tier enumeration."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class IsolationLevel(Enum):
    """Data isolation level enumeration."""
    SHARED = "shared"  # Shared database, logical separation
    DEDICATED_SCHEMA = "dedicated_schema"  # Dedicated schema per tenant
    DEDICATED_DATABASE = "dedicated_database"  # Dedicated database per tenant
    DEDICATED_INSTANCE = "dedicated_instance"  # Dedicated instance per tenant


class BillingModel(Enum):
    """Billing model enumeration."""
    FREE = "free"
    USAGE_BASED = "usage_based"
    SUBSCRIPTION = "subscription"
    HYBRID = "hybrid"
    ENTERPRISE = "enterprise"


@dataclass
class TenantLimits:
    """Tenant resource limits."""
    max_collections: int = 10
    max_documents_per_collection: int = 10000
    max_storage_gb: float = 1.0
    max_queries_per_hour: int = 1000
    max_concurrent_users: int = 10
    max_api_calls_per_day: int = 10000
    max_embedding_dimensions: int = 1536
    custom_limits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantUsage:
    """Tenant usage tracking."""
    collections_count: int = 0
    documents_count: int = 0
    storage_used_gb: float = 0.0
    queries_this_hour: int = 0
    queries_this_day: int = 0
    queries_this_month: int = 0
    active_users: int = 0
    api_calls_today: int = 0
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    usage_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TenantConfig:
    """Tenant-specific configuration."""
    features_enabled: Set[str] = field(default_factory=set)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    branding: Dict[str, str] = field(default_factory=dict)
    integrations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security_settings: Dict[str, Any] = field(default_factory=dict)
    notification_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Tenant:
    """Tenant representation."""
    tenant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    domain: Optional[str] = None
    tier: TenantTier = TenantTier.FREE
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    billing_model: BillingModel = BillingModel.FREE
    limits: TenantLimits = field(default_factory=TenantLimits)
    usage: TenantUsage = field(default_factory=TenantUsage)
    config: TenantConfig = field(default_factory=TenantConfig)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    subscription_expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_subscription_active(self) -> bool:
        """Check if subscription is active."""
        if self.subscription_expires_at is None:
            return True  # No expiration set
        return datetime.now(timezone.utc) < self.subscription_expires_at
    
    def is_within_limits(self, resource: str, requested_amount: int = 1) -> bool:
        """Check if tenant is within resource limits."""
        if resource == "collections":
            return self.usage.collections_count + requested_amount <= self.limits.max_collections
        elif resource == "documents":
            return self.usage.documents_count + requested_amount <= self.limits.max_documents_per_collection
        elif resource == "queries_hour":
            return self.usage.queries_this_hour + requested_amount <= self.limits.max_queries_per_hour
        elif resource == "api_calls_day":
            return self.usage.api_calls_today + requested_amount <= self.limits.max_api_calls_per_day
        elif resource == "concurrent_users":
            return self.usage.active_users + requested_amount <= self.limits.max_concurrent_users
        else:
            return True


class TenantManager:
    """Manages multi-tenant operations."""
    
    def __init__(
        self,
        security_manager: SecurityManager,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[AdvancedMetricsCollector] = None
    ):
        """Initialize tenant manager."""
        self.security_manager = security_manager
        self.logger = logger or AIPrishtinaLogger(name="tenant_manager")
        self.metrics = metrics or AdvancedMetricsCollector(logger)
        
        # Tenant storage
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_users: Dict[str, Set[str]] = {}  # tenant_id -> user_ids
        self.user_tenants: Dict[str, str] = {}  # user_id -> tenant_id
        
        # Tier configurations
        self.tier_configs = {
            TenantTier.FREE: TenantLimits(
                max_collections=3,
                max_documents_per_collection=1000,
                max_storage_gb=0.1,
                max_queries_per_hour=100,
                max_concurrent_users=2,
                max_api_calls_per_day=1000
            ),
            TenantTier.BASIC: TenantLimits(
                max_collections=10,
                max_documents_per_collection=10000,
                max_storage_gb=1.0,
                max_queries_per_hour=1000,
                max_concurrent_users=10,
                max_api_calls_per_day=10000
            ),
            TenantTier.PROFESSIONAL: TenantLimits(
                max_collections=50,
                max_documents_per_collection=100000,
                max_storage_gb=10.0,
                max_queries_per_hour=10000,
                max_concurrent_users=50,
                max_api_calls_per_day=100000
            ),
            TenantTier.ENTERPRISE: TenantLimits(
                max_collections=1000,
                max_documents_per_collection=1000000,
                max_storage_gb=100.0,
                max_queries_per_hour=100000,
                max_concurrent_users=1000,
                max_api_calls_per_day=1000000
            )
        }
        
        # Background tasks
        self.usage_tracking_task: Optional[asyncio.Task] = None
        self.billing_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start tenant manager."""
        await self.logger.info("Starting Tenant Manager")
        
        # Start background tasks
        self.usage_tracking_task = asyncio.create_task(self._usage_tracking_loop())
        self.billing_task = asyncio.create_task(self._billing_loop())
        
        await self.logger.info("Tenant Manager started")
    
    async def stop(self):
        """Stop tenant manager."""
        # Cancel background tasks
        for task in [self.usage_tracking_task, self.billing_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        await self.logger.info("Tenant Manager stopped")
    
    async def create_tenant(
        self,
        name: str,
        tier: TenantTier = TenantTier.FREE,
        domain: Optional[str] = None,
        admin_user_id: Optional[str] = None
    ) -> Tenant:
        """Create a new tenant."""
        try:
            # Create tenant
            tenant = Tenant(
                name=name,
                domain=domain,
                tier=tier,
                limits=self.tier_configs[tier]
            )
            
            # Set isolation level based on tier
            if tier in [TenantTier.ENTERPRISE, TenantTier.CUSTOM]:
                tenant.isolation_level = IsolationLevel.DEDICATED_DATABASE
            elif tier == TenantTier.PROFESSIONAL:
                tenant.isolation_level = IsolationLevel.DEDICATED_SCHEMA
            else:
                tenant.isolation_level = IsolationLevel.SHARED
            
            # Store tenant
            self.tenants[tenant.tenant_id] = tenant
            self.tenant_users[tenant.tenant_id] = set()
            
            # Add admin user if provided
            if admin_user_id:
                await self.add_user_to_tenant(tenant.tenant_id, admin_user_id, "admin")
            
            await self.logger.info(f"Created tenant: {name} ({tenant.tenant_id})")
            await self.metrics.record_metric("tenants.created", 1)
            
            return tenant
            
        except Exception as e:
            await self.logger.error(f"Failed to create tenant: {str(e)}")
            raise MultiTenancyError(f"Failed to create tenant: {str(e)}")
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
    
    async def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain."""
        for tenant in self.tenants.values():
            if tenant.domain == domain:
                return tenant
        return None
    
    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """Update tenant configuration."""
        try:
            if tenant_id not in self.tenants:
                return False
            
            tenant = self.tenants[tenant_id]
            
            # Update allowed fields
            if "name" in updates:
                tenant.name = updates["name"]
            if "tier" in updates:
                new_tier = TenantTier(updates["tier"])
                tenant.tier = new_tier
                tenant.limits = self.tier_configs[new_tier]
            if "config" in updates:
                tenant.config.custom_settings.update(updates["config"])
            
            tenant.updated_at = datetime.now(timezone.utc)
            
            await self.logger.info(f"Updated tenant: {tenant_id}")
            return True
            
        except Exception as e:
            await self.logger.error(f"Failed to update tenant {tenant_id}: {str(e)}")
            return False
    
    async def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        try:
            if tenant_id not in self.tenants:
                return False
            
            # Remove all users from tenant
            if tenant_id in self.tenant_users:
                for user_id in list(self.tenant_users[tenant_id]):
                    await self.remove_user_from_tenant(tenant_id, user_id)
            
            # Delete tenant
            del self.tenants[tenant_id]
            if tenant_id in self.tenant_users:
                del self.tenant_users[tenant_id]
            
            await self.logger.info(f"Deleted tenant: {tenant_id}")
            await self.metrics.record_metric("tenants.deleted", 1)
            
            return True
            
        except Exception as e:
            await self.logger.error(f"Failed to delete tenant {tenant_id}: {str(e)}")
            return False
    
    async def add_user_to_tenant(self, tenant_id: str, user_id: str, role: str = "user") -> bool:
        """Add user to tenant."""
        try:
            if tenant_id not in self.tenants:
                return False
            
            # Check if tenant is within user limits
            tenant = self.tenants[tenant_id]
            if not tenant.is_within_limits("concurrent_users", 1):
                await self.logger.warning(f"Tenant {tenant_id} at user limit")
                return False
            
            # Add user to tenant
            self.tenant_users[tenant_id].add(user_id)
            self.user_tenants[user_id] = tenant_id
            
            # Update usage
            tenant.usage.active_users = len(self.tenant_users[tenant_id])
            
            await self.logger.info(f"Added user {user_id} to tenant {tenant_id}")
            return True
            
        except Exception as e:
            await self.logger.error(f"Failed to add user to tenant: {str(e)}")
            return False
    
    async def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> bool:
        """Remove user from tenant."""
        try:
            if tenant_id in self.tenant_users:
                self.tenant_users[tenant_id].discard(user_id)
            
            if user_id in self.user_tenants:
                del self.user_tenants[user_id]
            
            # Update usage
            if tenant_id in self.tenants:
                tenant = self.tenants[tenant_id]
                tenant.usage.active_users = len(self.tenant_users.get(tenant_id, set()))
            
            await self.logger.info(f"Removed user {user_id} from tenant {tenant_id}")
            return True
            
        except Exception as e:
            await self.logger.error(f"Failed to remove user from tenant: {str(e)}")
            return False
    
    async def get_user_tenant(self, user_id: str) -> Optional[str]:
        """Get tenant ID for user."""
        return self.user_tenants.get(user_id)
    
    async def check_tenant_access(self, user_id: str, tenant_id: str) -> bool:
        """Check if user has access to tenant."""
        user_tenant = await self.get_user_tenant(user_id)
        return user_tenant == tenant_id
    
    async def track_usage(self, tenant_id: str, resource: str, amount: int = 1):
        """Track resource usage for tenant."""
        if tenant_id not in self.tenants:
            return
        
        tenant = self.tenants[tenant_id]
        
        if resource == "query":
            tenant.usage.queries_this_hour += amount
            tenant.usage.queries_this_day += amount
            tenant.usage.queries_this_month += amount
        elif resource == "api_call":
            tenant.usage.api_calls_today += amount
        elif resource == "storage":
            tenant.usage.storage_used_gb += amount
        elif resource == "document":
            tenant.usage.documents_count += amount
        elif resource == "collection":
            tenant.usage.collections_count += amount
        
        tenant.usage.last_activity = datetime.now(timezone.utc)
        
        # Record metrics
        await self.metrics.record_metric(f"tenant.{resource}.usage", amount)
        
        await self.logger.debug(f"Tracked {resource} usage for tenant {tenant_id}: {amount}")
    
    async def check_resource_limit(self, tenant_id: str, resource: str, requested_amount: int = 1) -> bool:
        """Check if tenant can use requested amount of resource."""
        if tenant_id not in self.tenants:
            return False
        
        tenant = self.tenants[tenant_id]
        
        # Check if tenant is active and subscription is valid
        if not tenant.is_active or not tenant.is_subscription_active():
            return False
        
        return tenant.is_within_limits(resource, requested_amount)
    
    async def _usage_tracking_loop(self):
        """Background task for usage tracking and cleanup."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                for tenant in self.tenants.values():
                    # Reset hourly counters
                    if current_time.hour != tenant.usage.last_activity.hour:
                        tenant.usage.queries_this_hour = 0
                    
                    # Reset daily counters
                    if current_time.date() != tenant.usage.last_activity.date():
                        tenant.usage.queries_this_day = 0
                        tenant.usage.api_calls_today = 0
                    
                    # Reset monthly counters
                    if current_time.month != tenant.usage.last_activity.month:
                        tenant.usage.queries_this_month = 0
                
                await asyncio.sleep(3600)  # Run every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Usage tracking error: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _billing_loop(self):
        """Background task for billing and subscription management."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                for tenant in self.tenants.values():
                    # Check subscription expiration
                    if (tenant.subscription_expires_at and 
                        current_time > tenant.subscription_expires_at):
                        
                        # Downgrade to free tier or deactivate
                        if tenant.tier != TenantTier.FREE:
                            tenant.tier = TenantTier.FREE
                            tenant.limits = self.tier_configs[TenantTier.FREE]
                            await self.logger.warning(f"Tenant {tenant.tenant_id} subscription expired")
                
                await asyncio.sleep(86400)  # Run daily
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Billing loop error: {str(e)}")
                await asyncio.sleep(86400)
    
    async def get_tenant_analytics(self, tenant_id: str) -> Dict[str, Any]:
        """Get analytics for a specific tenant."""
        if tenant_id not in self.tenants:
            return {}
        
        tenant = self.tenants[tenant_id]
        
        return {
            "tenant_id": tenant_id,
            "name": tenant.name,
            "tier": tenant.tier.value,
            "usage": {
                "collections": tenant.usage.collections_count,
                "documents": tenant.usage.documents_count,
                "storage_gb": tenant.usage.storage_used_gb,
                "queries_today": tenant.usage.queries_this_day,
                "queries_this_month": tenant.usage.queries_this_month,
                "active_users": tenant.usage.active_users,
                "api_calls_today": tenant.usage.api_calls_today
            },
            "limits": {
                "max_collections": tenant.limits.max_collections,
                "max_documents": tenant.limits.max_documents_per_collection,
                "max_storage_gb": tenant.limits.max_storage_gb,
                "max_queries_hour": tenant.limits.max_queries_per_hour,
                "max_users": tenant.limits.max_concurrent_users,
                "max_api_calls_day": tenant.limits.max_api_calls_per_day
            },
            "utilization": {
                "collections_percent": (tenant.usage.collections_count / tenant.limits.max_collections) * 100,
                "storage_percent": (tenant.usage.storage_used_gb / tenant.limits.max_storage_gb) * 100,
                "users_percent": (tenant.usage.active_users / tenant.limits.max_concurrent_users) * 100
            },
            "subscription": {
                "active": tenant.is_subscription_active(),
                "expires_at": tenant.subscription_expires_at.isoformat() if tenant.subscription_expires_at else None
            }
        }
    
    async def get_all_tenants_summary(self) -> Dict[str, Any]:
        """Get summary of all tenants."""
        total_tenants = len(self.tenants)
        active_tenants = len([t for t in self.tenants.values() if t.is_active])
        
        tier_distribution = {}
        for tier in TenantTier:
            tier_distribution[tier.value] = len([t for t in self.tenants.values() if t.tier == tier])
        
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "tier_distribution": tier_distribution,
            "total_users": len(self.user_tenants),
            "average_users_per_tenant": len(self.user_tenants) / max(1, total_tenants)
        }


class MultiTenancyError(AIPrishtinaError):
    """Exception raised for multi-tenancy errors."""
    pass
