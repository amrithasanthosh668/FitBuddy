from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # User details
    name = Column(String, nullable=True)
    user_code = Column(String, nullable=True)
    weight = Column(Float, nullable=True)

    # Existing details
    age = Column(Integer)
    goal = Column(String)
    level = Column(String)
    available_time = Column(String)

    # Workout intensity
    intensity = Column(String, nullable=True)

    fitness_plans = relationship(
        "FitnessPlan",
        back_populates="user"
    )


class FitnessPlan(Base):
    __tablename__ = "fitness_plans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    plan = Column(Text)

    feedback = Column(
        Text,
        nullable=True
    )

    updated_plan = Column(
        Text,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="fitness_plans"
    )