# Manages giveaway logic
from sqlalchemy.orm import Session
from bot.models import Giveaway, Participant, User
from datetime import datetime
import random

def create_giveaway(db: Session, title: str, description: str, end_date: datetime, message_id: int, chat_id: int) -> Giveaway:
    """Creates a new giveaway."""
    new_giveaway = Giveaway(
        title=title,
        description=description,
        end_date=end_date,
        message_id=message_id,
        chat_id=chat_id
    )
    db.add(new_giveaway)
    db.commit()
    db.refresh(new_giveaway)
    return new_giveaway

def get_giveaway(db: Session, giveaway_id: int) -> Giveaway | None:
    """Fetches a giveaway by its ID."""
    return db.query(Giveaway).filter(Giveaway.id == giveaway_id).first()

def add_participant(db: Session, giveaway_id: int, user_id: int) -> Participant | None:
    """Adds a user as a participant to a giveaway."""
    giveaway = get_giveaway(db, giveaway_id)
    if not giveaway:
        return None # Or raise an error

    # Check if user is already a participant
    existing_participant = db.query(Participant).filter(
        Participant.giveaway_id == giveaway_id,
        Participant.user_id == user_id
    ).first()
    if existing_participant:
        return existing_participant # Or indicate they are already participating

    new_participant = Participant(user_id=user_id, giveaway_id=giveaway_id)
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    return new_participant

def select_winner(db: Session, giveaway_id: int) -> User | None:
    """Selects a random winner for the giveaway."""
    giveaway = get_giveaway(db, giveaway_id)
    if not giveaway or giveaway.winner_id:
        return None # Giveaway doesn't exist or winner already selected

    participants = db.query(Participant).filter(Participant.giveaway_id == giveaway_id).all()
    if not participants:
        return None # No participants

    winner_participant = random.choice(participants)
    giveaway.winner_id = winner_participant.user_id
    db.commit()
    db.refresh(giveaway)
    return db.query(User).filter(User.id == giveaway.winner_id).first()

def get_active_giveaways(db: Session) -> list[Giveaway]:
    """Returns a list of all giveaways that have not ended and have no winner yet."""
    return db.query(Giveaway).filter(Giveaway.end_date > datetime.utcnow(), Giveaway.winner_id == None).all()

def get_user_by_telegram_id(db: Session, telegram_id: int) -> User | None:
    """Fetches a user by their Telegram ID."""
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(db: Session, telegram_id: int, username: str | None, first_name: str | None, last_name: str | None) -> User:
    """Creates a new user or returns existing user if telegram_id already exists."""
    existing_user = get_user_by_telegram_id(db, telegram_id)
    if existing_user:
        return existing_user

    new_user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
