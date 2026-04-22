from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class TicketStatus(enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_USER = "waiting_user"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=True)
    ad_username = Column(String, unique=True, index=True, nullable=False)
    ad_full_name = Column(String, nullable=True)
    ad_email = Column(String, nullable=True)
    ad_department = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tickets = relationship("Ticket", back_populates="user", lazy="select")
    
    def __repr__(self):
        return f"<User {self.ad_username}>"


class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_username = Column(String, unique=True, index=True, nullable=False)
    ad_full_name = Column(String, nullable=True)
    ad_email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assigned_tickets = relationship("Ticket", back_populates="assigned_admin", lazy="select")
    
    def __repr__(self):
        return f"<Admin {self.ad_username}>"


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.NEW)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM)
    
    messenger_chat_id = Column(String, nullable=True)
    messenger_message_id = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="tickets", lazy="select")
    assigned_admin = relationship("Admin", back_populates="assigned_tickets", lazy="select")
    
    def __repr__(self):
        return f"<Ticket #{self.id} - {self.subject}>"
