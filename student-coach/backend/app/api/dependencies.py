from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db as _get_db
from app.core.security import decode_token
from app.services.auth_service import AuthService
from app.models.user import User


def get_db():
    yield from _get_db()


async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    # Validate session not expired
    auth = AuthService(db)
    session = auth.validate_session(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid")
    user = db.query(User).get(int(sub))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserSession


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    token = authorization.replace('Bearer ', '')
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    user_id = int(payload.get('sub'))
    # validate active session
    session = db.query(UserSession).filter(UserSession.access_token == token).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expirée")
    user = db.query(User).get(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte inactif")
    return user
