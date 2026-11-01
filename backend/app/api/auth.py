from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.user import User

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    ChangePasswordRequest
)

from app.api.dependencies import get_current_user

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.services.audit_service import record_audit_safely


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_username = db.query(User).filter(
        User.username == request.username
    ).first()

    if existing_username:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )


    existing_email = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )


    password_hash = hash_password(
        request.password
    )


    user = User(
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        role="USER",
        is_active=True
    )


    db.add(user)

    db.commit()

    db.refresh(user)


    return user


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == request.username
    ).first()


    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )


    if not verify_password(
        request.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )


    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )


    access_token = create_access_token(
        {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role
        }
    )

    record_audit_safely(
        db,
        actor=user,
        action="USER_LOGIN",
        resource_type="USER",
        resource_id=user.id,
        summary=f"Operator '{user.username}' authenticated",
    )


    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK
)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(
        request.current_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    if request.new_password == request.current_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from the current password"
        )

    current_user.password_hash = hash_password(request.new_password)

    db.commit()

    record_audit_safely(
        db,
        actor=current_user,
        action="USER_PASSWORD_CHANGED",
        resource_type="USER",
        resource_id=current_user.id,
        summary=f"Operator '{current_user.username}' changed their password",
    )

    return {"message": "Password changed successfully"}