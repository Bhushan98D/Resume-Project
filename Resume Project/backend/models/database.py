"""
Database models and configuration for the Resume Relevance Check System.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///resume_checker.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Resume(Base):
    """Model for storing resume information."""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # PDF or DOCX
    extracted_text = Column(Text, nullable=False)
    parsed_data = Column(Text)  # JSON string of structured data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobDescription(Base):
    """Model for storing job description information."""
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255))
    description = Column(Text, nullable=False)
    must_have_skills = Column(Text)  # JSON string
    nice_to_have_skills = Column(Text)  # JSON string
    qualifications = Column(Text)  # JSON string
    experience_required = Column(String(100))
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Evaluation(Base):
    """Model for storing evaluation results."""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, nullable=False)
    job_description_id = Column(Integer, nullable=False)
    relevance_score = Column(Float, nullable=False)  # 0-100
    hard_match_score = Column(Float, nullable=False)  # 0-100
    semantic_match_score = Column(Float, nullable=False)  # 0-100
    education_match_score = Column(Float, nullable=False)  # 0-100
    experience_match_score = Column(Float, nullable=False)  # 0-100
    verdict = Column(String(20), nullable=False)  # High/Medium/Low
    missing_skills = Column(Text)  # JSON string
    suggestions = Column(Text)  # JSON string
    detailed_report = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Model for storing user information (for admin panel)."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Create all tables
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


# Database dependency
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")
