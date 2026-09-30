from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, String, Integer, Float, Text, DateTime, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session, relationship
from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    goal: Mapped[str] = mapped_column(String(50))
    intensity: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    plans: Mapped[list["Plan"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    original_plan: Mapped[str] = mapped_column(Text)
    updated_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    user: Mapped["User"] = relationship(back_populates="plans")

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_user(db: Session, user_data: dict) -> User:
    user = db.scalar(select(User).where(User.user_id == user_data["user_id"]))
    if user:
        for key, value in user_data.items():
            setattr(user, key, value)
    else:
        user = User(**user_data)
        db.add(user)
    db.commit()
    db.refresh(user)
    return user

def save_plan(db: Session, user: User, original_plan: str, nutrition_tip: str) -> Plan:
    plan = Plan(user_id=user.id, original_plan=original_plan, nutrition_tip=nutrition_tip)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

def get_user(db: Session, user_id: str) -> Optional[User]:
    return db.scalar(select(User).where(User.user_id == user_id))

def get_latest_plan(db: Session, user: User) -> Optional[Plan]:
    return db.scalar(select(Plan).where(Plan.user_id == user.id).order_by(Plan.id.desc()))

def update_plan(db: Session, plan: Plan, updated_plan: str, feedback: str) -> Plan:
    plan.updated_plan = updated_plan
    plan.feedback = feedback
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    return plan

def get_all_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())

def delete_user(db: Session, user_id: str) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
