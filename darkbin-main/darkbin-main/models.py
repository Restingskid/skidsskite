"""
Database models for skids.rest
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
import uuid

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'users'
    
    # Primary fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True, index=True)
    
    # Role & Permissions
    role = Column(String(20), default='user')  # admin, manager, mod, council, clique, user
    
    # Profile
    bio = Column(Text, default='')
    profile_image = Column(String(500), default='')
    banner_url = Column(String(500), default='')
    username_color = Column(String(7), default='#ff69b4')
    
    # Stats
    paste_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    reputation_points = Column(Integer, default=0)
    follower_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    
    # Timestamps
    joined_date = Column(DateTime, default=datetime.utcnow)
    
    # Premium Subscription
    tier = Column(String(20), default='free')  # free, premium
    tier_status = Column(String(20), default='none')  # none, active, past_due, canceled
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    premium_expires_at = Column(DateTime, nullable=True)
    
    # Moderation
    is_banned = Column(Boolean, default=False)
    is_suspended = Column(Boolean, default=False)
    banned_until = Column(DateTime, nullable=True)
    suspended_until = Column(DateTime, nullable=True)
    ban_reason = Column(Text, nullable=True)
    suspension_reason = Column(Text, nullable=True)
    banned_by = Column(String(50), nullable=True)
    suspended_by = Column(String(50), nullable=True)
    banned_at = Column(DateTime, nullable=True)
    suspended_at = Column(DateTime, nullable=True)
    
    # Featured
    is_featured = Column(Boolean, default=False)


class Paste(Base):
    __tablename__ = 'pastes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(50), default='text')
    
    # Visibility & Expiration
    is_public = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Stats
    views = Column(Integer, default=0)
    
    # Timestamps
    created_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50), nullable=True)  # username or 'anonymous'
    
    # Moderation
    is_deleted = Column(Boolean, default=False)
    deleted_by = Column(String(50), nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    delete_reason = Column(Text, nullable=True)
    
    # Pinning
    is_pinned = Column(Boolean, default=False)
    pinned_by = Column(String(50), nullable=True)
    pinned_at = Column(DateTime, nullable=True)


class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50), nullable=False)  # username
    profile_user = Column(String(50), nullable=False)  # profile owner username


class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), nullable=True)  # username or null for guest
    email = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    status = Column(String(20), default='open')  # open, pending, closed
    priority = Column(String(20), default='normal')  # normal, urgent
    
    # Assignment
    assigned_to = Column(String(50), nullable=True)  # staff username
    
    # Notes (JSON array)
    notes = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), nullable=False)  # username
    username = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    room = Column(String(50), default='global')
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SecurityLog(Base):
    __tablename__ = 'security_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(50), nullable=False)  # login, register, paste_create, etc.
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String(50), nullable=True)
    success = Column(Boolean, default=True)
    additional_data = Column(JSON, nullable=True)