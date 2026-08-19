"""
Auth endpoints — signup, login, token management, password operations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordConfirm,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)
from app.models.orm.admin_user import AdminUser
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(
    body: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.signup(
        email=body.email,
        password=body.password,
        name=body.name,
        role=body.role,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.login(email=body.email, password=body.password)


@router.get("/me")
async def get_me(
    current_user: AdminUser = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.refresh_token(body.refresh_token)


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.change_password(
        user_id=str(current_user.id),
        old_password=body.old_password,
        new_password=body.new_password,
    )


@router.post("/reset-password")
async def reset_password_request(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.reset_password_request(email=body.email)


@router.post("/reset-password/confirm")
async def reset_password_confirm(
    body: ResetPasswordConfirm,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.reset_password_confirm(
        token=body.token,
        new_password=body.new_password,
    )
