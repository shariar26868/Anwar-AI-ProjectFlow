import enum
from sqlalchemy import Column, Integer, String, Enum
from app.db import Base


class RoleEnum(str, enum.Enum):
    ai_analyst = "ai_analyst"
    developer = "developer"
    business_owner = "business_owner"
    team_lead = "team_lead"
    management = "management"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    department = Column(String)
