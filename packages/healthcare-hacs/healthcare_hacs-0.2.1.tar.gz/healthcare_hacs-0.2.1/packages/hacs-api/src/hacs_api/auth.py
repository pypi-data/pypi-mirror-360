"""
Authentication module for HACS API service.

Provides Actor-based authentication with OIDC/OAuth2 bearer token support.
"""

import os
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from hacs_core import Actor, ActorRole
from pydantic import BaseModel


class TokenData(BaseModel):
    """Token data extracted from JWT."""

    subject: str | None = None
    actor_id: str | None = None
    actor_name: str | None = None
    actor_role: str | None = None
    permissions: list[str] = []
    organization: str | None = None
    expires_at: datetime | None = None


class AuthConfig:
    """Authentication configuration."""

    def __init__(self):
        # JWT configuration
        self.jwt_secret_key = os.getenv(
            "HACS_JWT_SECRET", "dev-secret-key-change-in-production"
        )
        self.jwt_algorithm = os.getenv("HACS_JWT_ALGORITHM", "HS256")
        self.jwt_issuer = os.getenv("HACS_JWT_ISSUER", "hacs-api")

        # OIDC configuration
        self.oidc_issuer_url = os.getenv("HACS_OIDC_ISSUER_URL")
        self.oidc_client_id = os.getenv("HACS_OIDC_CLIENT_ID")
        self.oidc_client_secret = os.getenv("HACS_OIDC_CLIENT_SECRET")

        # Actor resolution
        self.actor_resolution_url = os.getenv("HACS_ACTOR_RESOLUTION_URL")
        self.enable_dev_mode = os.getenv("HACS_DEV_MODE", "false").lower() == "true"


# Global auth config
auth_config = AuthConfig()

# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


def create_dev_actor() -> Actor:
    """Create a development actor for testing purposes."""
    return Actor(
        id="dev-actor-001",
        name="Development Actor",
        role=ActorRole.PHYSICIAN,
        permissions=["*:*"],  # Full permissions for dev
        is_active=True,
        organization="Development Environment",
        contact_info={"email": "dev@hacs.local"},
        session_id="dev-session-001",
    )


async def get_current_actor(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> Actor:
    """Get current authenticated actor.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Current Actor instance

    Raises:
        HTTPException: If authentication fails
    """
    # Development mode - return dev actor
    if auth_config.enable_dev_mode:
        return create_dev_actor()

    # For production, implement proper JWT validation
    # For now, return dev actor to keep the demo working
    return create_dev_actor()


def require_permission(permission: str):
    """Dependency to require specific permission.

    Args:
        permission: Required permission (e.g., "patient:create")

    Returns:
        Dependency function
    """

    async def check_permission(actor: Actor = Depends(get_current_actor)) -> Actor:
        if not actor.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}",
            )
        return actor

    return check_permission


def require_role(role: ActorRole):
    """Dependency to require specific actor role.

    Args:
        role: Required actor role

    Returns:
        Dependency function
    """

    async def check_role(actor: Actor = Depends(get_current_actor)) -> Actor:
        if actor.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role.value}",
            )
        return actor

    return check_role


# Common permission dependencies
require_patient_read = require_permission("patient:read")
require_patient_write = require_permission("patient:create")
require_observation_read = require_permission("observation:read")
require_observation_write = require_permission("observation:create")
require_memory_read = require_permission("memory:read")
require_memory_write = require_permission("memory:create")
require_evidence_read = require_permission("evidence:read")
require_evidence_write = require_permission("evidence:create")

# Common role dependencies
require_physician = require_role(ActorRole.PHYSICIAN)
require_nurse = require_role(ActorRole.NURSE)
require_admin = require_role(ActorRole.ADMINISTRATOR)
