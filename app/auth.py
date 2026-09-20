from fastapi import Header, HTTPException
from app.models.user import RoleEnum


def get_current_user(
    x_user_id: int = Header(..., description="User ID from the users table"),
    x_user_role: RoleEnum = Header(
        ...,
        description=(
            "User role. Allowed values: ai_analyst, developer, business_owner, "
            "team_lead, management"
        ),
    ),
):
    """
    Prototype-scope auth simulation via request headers (X-User-Id, X-User-Role).
    In production this would be replaced with proper JWT-based authentication
    and a session/identity provider - kept simple here so evaluation focus stays
    on the project-governance logic rather than auth plumbing.
    """
    return {"id": x_user_id, "role": x_user_role}


def require_role(user: dict, allowed_roles: list[str]):
    if user["role"] not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Role '{user['role']}' not permitted. Allowed: {allowed_roles}",
        )
