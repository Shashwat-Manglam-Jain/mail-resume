from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import NeonBase


class Profile(NeonBase):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, default="")
    email = Column(String(255), nullable=False, default="")
    phone = Column(String(100), nullable=False, default="")
    location = Column(String(255), nullable=False, default="")
    linkedin = Column(String(500), nullable=False, default="")
    github = Column(String(500), nullable=False, default="")
    portfolio = Column(String(500), nullable=False, default="")
    education = Column(String(500), nullable=False, default="")
    graduation_year = Column(String(50), nullable=False, default="")
    experience_years = Column(String(50), nullable=False, default="")
    company_1_name = Column(String(255), nullable=False, default="")
    company_1_role = Column(String(255), nullable=False, default="")
    company_1_location = Column(String(255), nullable=False, default="")
    company_1_duration = Column(String(255), nullable=False, default="")
    company_2_name = Column(String(255), nullable=False, default="")
    company_2_role = Column(String(255), nullable=False, default="")
    company_2_location = Column(String(255), nullable=False, default="")
    company_2_duration = Column(String(255), nullable=False, default="")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Role(NeonBase):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    previous_title = Column(String(255), nullable=False, default="")
    summary = Column(Text, nullable=False, default="")
    coursework = Column(Text, nullable=False, default="")
    is_active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    skills = relationship("RoleSkill", back_populates="role", cascade="all, delete-orphan", order_by="RoleSkill.sort_order")
    experiences = relationship("RoleExperience", back_populates="role", cascade="all, delete-orphan", order_by="RoleExperience.position_index")
    achievements = relationship("RoleAchievement", back_populates="role", cascade="all, delete-orphan", order_by="RoleAchievement.sort_order")
    focus_areas = relationship("RoleFocusArea", back_populates="role", cascade="all, delete-orphan", order_by="RoleFocusArea.sort_order")


class RoleSkill(NeonBase):
    __tablename__ = "role_skills"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)
    skills = Column(JSON, nullable=False, default=list)
    sort_order = Column(Integer, nullable=False, default=0)

    role = relationship("Role", back_populates="skills")


class RoleExperience(NeonBase):
    __tablename__ = "role_experiences"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    position_index = Column(Integer, nullable=False, default=0)
    bullets = Column(JSON, nullable=False, default=list)
    client_name = Column(String(255), nullable=True, default="")
    client_location = Column(String(255), nullable=True, default="")
    min_years = Column(Integer, nullable=True, default=1)

    role = relationship("Role", back_populates="experiences")


class RoleAchievement(NeonBase):
    __tablename__ = "role_achievements"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    role = relationship("Role", back_populates="achievements")


class RoleFocusArea(NeonBase):
    __tablename__ = "role_focus_areas"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    area = Column(String(500), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    role = relationship("Role", back_populates="focus_areas")
