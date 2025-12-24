from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User, UserSession
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.config.settings import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str):
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def create_session(self, user_id: int, device_id: str, device_type: str, ip_address: str):
        access_token, access_expires = create_access_token({"sub": str(user_id)})
        refresh_token, refresh_expires = create_refresh_token({"sub": str(user_id)})
        session = UserSession(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            device_id=device_id,
            device_type=device_type,
            ip_address=ip_address,
            expires_at=access_expires,
        )
        self.db.add(session)
        self.db.commit()
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def validate_session(self, access_token: str):
        session = self.db.query(UserSession).filter(
            UserSession.access_token == access_token,
            UserSession.expires_at > datetime.utcnow(),
        ).first()
        return session

    def logout(self, access_token: str):
        session = self.db.query(UserSession).filter(UserSession.access_token == access_token).first()
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False
