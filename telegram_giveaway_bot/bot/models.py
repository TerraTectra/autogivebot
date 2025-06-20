from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from config.settings import DATABASE_URL

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    participations = relationship("Participant", back_populates="user")

class Giveaway(Base):
    __tablename__ = "giveaways"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    end_date = Column(DateTime, nullable=False)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    message_id = Column(Integer, nullable=True)  # To store the ID of the giveaway message
    chat_id = Column(Integer, nullable=True) # To store the Chat ID where the giveaway was created

    winner = relationship("User")
    participants = relationship("Participant", back_populates="giveaway")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    giveaway_id = Column(Integer, ForeignKey("giveaways.id"), nullable=False)
    participated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="participations")
    giveaway = relationship("Giveaway", back_populates="participants")


# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# init_db() function is removed as schema creation is now handled by Alembic migrations.
# Users should use 'alembic upgrade head' to apply migrations.

# The if __name__ == "__main__": block for manual init_db() execution is also removed.
