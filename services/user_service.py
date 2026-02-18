from sqlalchemy.orm import Session
from models.User import User

class UserService:
    @staticmethod
    def get_user(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def create_user(db: Session, username: str, email: str, hashed_password: str = "hashed_password_here"):
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
