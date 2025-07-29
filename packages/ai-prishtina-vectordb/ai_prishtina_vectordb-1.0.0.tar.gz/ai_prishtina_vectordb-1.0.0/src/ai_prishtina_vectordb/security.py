"""
Enhanced security features for AI Prishtina VectorDB.

This module provides comprehensive security capabilities including
authentication, authorization, encryption, audit logging, and compliance.
"""

import hashlib
import hmac
import secrets
import jwt
import bcrypt
import time
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from .logger import AIPrishtinaLogger
from .metrics import AdvancedMetricsCollector
from .exceptions import AIPrishtinaError


class SecurityLevel(Enum):
    """Security level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionType(Enum):
    """Permission type enumeration."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"
    CREATE = "create"
    UPDATE = "update"


class AuthenticationMethod(Enum):
    """Authentication method enumeration."""
    PASSWORD = "password"
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    CERTIFICATE = "certificate"
    MULTI_FACTOR = "multi_factor"


@dataclass
class SecurityConfig:
    """Security configuration."""
    encryption_enabled: bool = True
    authentication_required: bool = True
    authorization_enabled: bool = True
    audit_logging: bool = True
    password_policy_enabled: bool = True
    session_timeout_minutes: int = 60
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    jwt_secret_key: Optional[str] = None
    jwt_expiration_hours: int = 24
    encryption_key: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.HIGH
    compliance_mode: Optional[str] = None  # GDPR, HIPAA, SOX, etc.


@dataclass
class User:
    """Security user representation."""
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: Set[str] = field(default_factory=set)
    permissions: Set[PermissionType] = field(default_factory=set)
    is_active: bool = True
    is_locked: bool = False
    failed_login_attempts: int = 0
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """User session representation."""
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1))
    is_active: bool = True
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now(timezone.utc) > self.expires_at


@dataclass
class AuditLogEntry:
    """Audit log entry."""
    log_id: str
    user_id: str
    action: str
    resource: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)


class PasswordPolicy:
    """Password policy enforcement."""
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True,
        max_age_days: int = 90
    ):
        """Initialize password policy."""
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.max_age_days = max_age_days
        self.special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password against policy."""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digits and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special and not any(c in self.special_chars for c in password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors


class EncryptionManager:
    """Handles data encryption and decryption."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize encryption manager."""
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
        
        # Generate RSA key pair for asymmetric encryption
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data using symmetric encryption."""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using symmetric encryption."""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def encrypt_with_public_key(self, data: str) -> str:
        """Encrypt data using RSA public key."""
        encrypted_data = self.public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_with_private_key(self, encrypted_data: str) -> str:
        """Decrypt data using RSA private key."""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_data.decode()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode(), hashed.encode())


class AuthenticationManager:
    """Handles user authentication."""
    
    def __init__(
        self,
        config: SecurityConfig,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize authentication manager."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="auth_manager")
        self.encryption_manager = EncryptionManager(config.encryption_key)
        self.password_policy = PasswordPolicy()
        
        # User storage (in production, use a proper database)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> user_id
        
        # JWT configuration
        self.jwt_secret = config.jwt_secret_key or secrets.token_urlsafe(32)
    
    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: Optional[Set[str]] = None
    ) -> Tuple[bool, str]:
        """Register a new user."""
        try:
            # Validate password
            if self.config.password_policy_enabled:
                is_valid, errors = self.password_policy.validate_password(password)
                if not is_valid:
                    return False, "; ".join(errors)
            
            # Check if user already exists
            if any(u.username == username or u.email == email for u in self.users.values()):
                return False, "User already exists"
            
            # Create user
            user_id = secrets.token_urlsafe(16)
            password_hash = self.encryption_manager.hash_password(password)
            
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                roles=roles or set()
            )
            
            self.users[user_id] = user
            
            await self.logger.info(f"User registered: {username}")
            return True, user_id
            
        except Exception as e:
            await self.logger.error(f"User registration failed: {str(e)}")
            return False, str(e)
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Authenticate user with username and password."""
        try:
            # Find user
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                await self.logger.warning(f"Authentication failed: user not found - {username}")
                return False, None
            
            # Check if user is locked
            if user.is_locked:
                await self.logger.warning(f"Authentication failed: user locked - {username}")
                return False, None
            
            # Check if user is active
            if not user.is_active:
                await self.logger.warning(f"Authentication failed: user inactive - {username}")
                return False, None
            
            # Verify password
            if not self.encryption_manager.verify_password(password, user.password_hash):
                user.failed_login_attempts += 1
                
                # Lock user if too many failed attempts
                if user.failed_login_attempts >= self.config.max_login_attempts:
                    user.is_locked = True
                    await self.logger.warning(f"User locked due to failed attempts: {username}")
                
                await self.logger.warning(f"Authentication failed: invalid password - {username}")
                return False, None
            
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = datetime.now(timezone.utc)
            
            await self.logger.info(f"User authenticated: {username}")
            return True, user.user_id
            
        except Exception as e:
            await self.logger.error(f"Authentication error: {str(e)}")
            return False, None
    
    async def create_session(self, user_id: str, ip_address: Optional[str] = None) -> str:
        """Create a new user session."""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self.config.session_timeout_minutes)
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            expires_at=expires_at,
            ip_address=ip_address
        )
        
        self.sessions[session_id] = session
        
        await self.logger.debug(f"Session created: {session_id}")
        return session_id
    
    async def validate_session(self, session_id: str) -> Optional[str]:
        """Validate session and return user ID."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        if not session.is_active or session.is_expired():
            del self.sessions[session_id]
            return None
        
        return session.user_id
    
    async def create_jwt_token(self, user_id: str) -> str:
        """Create JWT token for user."""
        payload = {
            "user_id": user_id,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=self.config.jwt_expiration_hours)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token
    
    async def validate_jwt_token(self, token: str) -> Optional[str]:
        """Validate JWT token and return user ID."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            await self.logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            await self.logger.warning("Invalid JWT token")
            return None
    
    async def create_api_key(self, user_id: str) -> str:
        """Create API key for user."""
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        self.api_keys[api_key] = user_id
        
        await self.logger.info(f"API key created for user: {user_id}")
        return api_key
    
    async def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return user ID."""
        return self.api_keys.get(api_key)


class AuthorizationManager:
    """Handles user authorization and permissions."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize authorization manager."""
        self.logger = logger or AIPrishtinaLogger(name="authz_manager")
        
        # Role-based permissions
        self.role_permissions: Dict[str, Set[PermissionType]] = {
            "admin": {PermissionType.READ, PermissionType.WRITE, PermissionType.DELETE, PermissionType.ADMIN},
            "editor": {PermissionType.READ, PermissionType.WRITE, PermissionType.CREATE, PermissionType.UPDATE},
            "viewer": {PermissionType.READ},
            "guest": set()
        }
        
        # Resource-based permissions
        self.resource_permissions: Dict[str, Dict[str, Set[PermissionType]]] = {}
    
    async def check_permission(
        self,
        user: User,
        resource: str,
        permission: PermissionType
    ) -> bool:
        """Check if user has permission for resource."""
        try:
            # Check direct user permissions
            if permission in user.permissions:
                return True
            
            # Check role-based permissions
            for role in user.roles:
                if role in self.role_permissions:
                    if permission in self.role_permissions[role]:
                        return True
            
            # Check resource-specific permissions
            if resource in self.resource_permissions:
                if user.user_id in self.resource_permissions[resource]:
                    if permission in self.resource_permissions[resource][user.user_id]:
                        return True
            
            return False
            
        except Exception as e:
            await self.logger.error(f"Permission check error: {str(e)}")
            return False
    
    async def grant_permission(
        self,
        user_id: str,
        resource: str,
        permission: PermissionType
    ):
        """Grant permission to user for resource."""
        if resource not in self.resource_permissions:
            self.resource_permissions[resource] = {}
        
        if user_id not in self.resource_permissions[resource]:
            self.resource_permissions[resource][user_id] = set()
        
        self.resource_permissions[resource][user_id].add(permission)
        
        await self.logger.info(f"Granted {permission.value} permission to user {user_id} for resource {resource}")
    
    async def revoke_permission(
        self,
        user_id: str,
        resource: str,
        permission: PermissionType
    ):
        """Revoke permission from user for resource."""
        if resource in self.resource_permissions:
            if user_id in self.resource_permissions[resource]:
                self.resource_permissions[resource][user_id].discard(permission)
                
                await self.logger.info(f"Revoked {permission.value} permission from user {user_id} for resource {resource}")


class AuditLogger:
    """Handles security audit logging."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize audit logger."""
        self.logger = logger or AIPrishtinaLogger(name="audit_logger")
        self.audit_logs: List[AuditLogEntry] = []
    
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        success: bool = True,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log a security-relevant action."""
        log_entry = AuditLogEntry(
            log_id=secrets.token_urlsafe(16),
            user_id=user_id,
            action=action,
            resource=resource,
            success=success,
            ip_address=ip_address,
            details=details or {}
        )
        
        self.audit_logs.append(log_entry)
        
        # Log to main logger
        level = "info" if success else "warning"
        await getattr(self.logger, level)(
            f"AUDIT: {action} on {resource} by {user_id} - {'SUCCESS' if success else 'FAILED'}"
        )
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditLogEntry]:
        """Get filtered audit logs."""
        filtered_logs = self.audit_logs
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
        
        if action:
            filtered_logs = [log for log in filtered_logs if log.action == action]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        
        return filtered_logs


class SecurityManager:
    """Main security manager coordinating all security features."""
    
    def __init__(
        self,
        config: SecurityConfig,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[AdvancedMetricsCollector] = None
    ):
        """Initialize security manager."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="security_manager")
        self.metrics = metrics or AdvancedMetricsCollector(logger)
        
        # Components
        self.auth_manager = AuthenticationManager(config, logger)
        self.authz_manager = AuthorizationManager(logger)
        self.audit_logger = AuditLogger(logger)
        self.encryption_manager = EncryptionManager(config.encryption_key)
    
    async def authenticate_request(
        self,
        auth_header: str,
        method: AuthenticationMethod = AuthenticationMethod.JWT_TOKEN
    ) -> Optional[str]:
        """Authenticate a request and return user ID."""
        try:
            if method == AuthenticationMethod.JWT_TOKEN:
                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]
                    return await self.auth_manager.validate_jwt_token(token)
            
            elif method == AuthenticationMethod.API_KEY:
                return await self.auth_manager.validate_api_key(auth_header)
            
            elif method == AuthenticationMethod.PASSWORD:
                # Handle session-based authentication
                return await self.auth_manager.validate_session(auth_header)
            
            return None
            
        except Exception as e:
            await self.logger.error(f"Authentication error: {str(e)}")
            return None
    
    async def authorize_request(
        self,
        user_id: str,
        resource: str,
        permission: PermissionType
    ) -> bool:
        """Authorize a request."""
        if user_id not in self.auth_manager.users:
            return False
        
        user = self.auth_manager.users[user_id]
        return await self.authz_manager.check_permission(user, resource, permission)
    
    async def secure_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if self.config.encryption_enabled:
            return self.encryption_manager.encrypt_data(data)
        return data
    
    async def unsecure_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if self.config.encryption_enabled:
            return self.encryption_manager.decrypt_data(encrypted_data)
        return encrypted_data
    
    async def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status."""
        return {
            "encryption_enabled": self.config.encryption_enabled,
            "authentication_required": self.config.authentication_required,
            "authorization_enabled": self.config.authorization_enabled,
            "audit_logging": self.config.audit_logging,
            "security_level": self.config.security_level.value,
            "active_sessions": len(self.auth_manager.sessions),
            "total_users": len(self.auth_manager.users),
            "audit_log_entries": len(self.audit_logger.audit_logs)
        }


class SecurityError(AIPrishtinaError):
    """Exception raised for security-related errors."""
    pass
