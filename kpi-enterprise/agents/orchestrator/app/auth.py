"""Auth + tenant extraction.

Demo mode: take tenant from `X-Tenant-Id` header. Default: tnt_demo.
Production mode (auth_mode="jwt"): verify JWT against JWKS, require
`tenant_id` claim, deny otherwise.
"""
from __future__ import annotations

import re
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from .config import settings

TENANT_PATTERN = re.compile(r"^tnt_[a-z0-9]{4,32}$")


def _extract_demo_tenant(x_tenant_id: str | None) -> str:
    if x_tenant_id is None:
        return settings.default_tenant
    if not TENANT_PATTERN.match(x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid tenant_id format: {x_tenant_id!r}",
        )
    return x_tenant_id


def _extract_jwt_tenant(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
        )
    # NOTE: jwt verification + claim extraction lives here in production.
    # For now we strictly refuse — production wiring is part of CP-104.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="JWT mode not yet implemented; set KPI_AUTH_MODE=demo",
    )


async def current_tenant(
    request: Request,
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-Id")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    if settings.auth_mode == "demo":
        tenant = _extract_demo_tenant(x_tenant_id)
    else:
        tenant = _extract_jwt_tenant(authorization)
    request.state.tenant_id = tenant
    return tenant


CurrentTenant = Annotated[str, Depends(current_tenant)]
