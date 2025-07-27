from __future__ import annotations

import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Index
from sqlalchemy.orm import relationship

from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ClassificationJob(Base):
    __tablename__ = "classification_jobs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User")


class ClassificationResult(Base):
    __tablename__ = "classification_results"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("classification_jobs.id"), nullable=False)
    text = Column(Text, nullable=False)
    label = Column(String(50))
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("ClassificationJob", backref="results")


class Model(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index("ix_models_name_version", "name", "version", unique=True),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    details = Column(Text)


class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
