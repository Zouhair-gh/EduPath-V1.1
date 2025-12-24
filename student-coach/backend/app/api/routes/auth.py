from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    device_id: str = Header(..., alias="X-Device-ID"),
    device_type: str = Header(..., alias="X-Device-Type"),
    user_agent: str = Header(None, alias="User-Agent"),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte désactivé")
    tokens = auth_service.create_session(user_id=user.id, device_id=device_id, device_type=device_type, ip_address="0.0.0.0")
    return tokens

@router.post("/logout")
async def logout(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    token = authorization.replace("Bearer ", "")
    auth_service = AuthService(db)
    success = auth_service.logout(token)
    if success:
        return {"message": "Déconnexion réussie"}
    else:
        raise HTTPException(status_code=404, detail="Session introuvable")
