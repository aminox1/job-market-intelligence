"""
Database models — SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, ForeignKey, Table
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


# Table d'association Many-to-Many entre Job et Skill
job_skill_association = Table(
    "job_skill",
    Base.metadata,
    Column("job_id", Integer, ForeignKey("jobs.id", ondelete="CASCADE")),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE")),
)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    remote_id = Column(String(255), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    company = Column(String(255))
    location = Column(String(255))
    country = Column(String(100))
    category = Column(String(100))
    job_type = Column(String(50))        # full-time, part-time, contract
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    description = Column(Text)
    url = Column(String(1000))
    source = Column(String(50))          # remotive, adzuna
    level = Column(String(50))           # junior, mid, senior
    remote_type = Column(String(50))     # remote, hybrid, onsite
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    skills = relationship(
        "Skill", secondary=job_skill_association, back_populates="jobs"
    )

    def __repr__(self):
        return f"<Job id={self.id} title='{self.title}' company='{self.company}'>"


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))       # language, framework, tool, cloud, ml_ai, etc.

    jobs = relationship(
        "Job", secondary=job_skill_association, back_populates="skills"
    )
    snapshots = relationship("TrendSnapshot", back_populates="skill", cascade="all, delete")

    def __repr__(self):
        return f"<Skill name='{self.name}' category='{self.category}'>"


class TrendSnapshot(Base):
    """Capture quotidienne du nombre d'offres par skill — pour les graphiques de tendances."""
    __tablename__ = "trend_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    count = Column(Integer, default=0)

    skill = relationship("Skill", back_populates="snapshots")

    def __repr__(self):
        return f"<TrendSnapshot skill_id={self.skill_id} date={self.date} count={self.count}>"
