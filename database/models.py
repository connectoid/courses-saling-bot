from datetime import datetime

from sqlalchemy import Table, Text, Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UseCourse(Base):
    __tablename__ = 'user_course'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('course.id'), primary_key=True)



class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    fname = Column(String, nullable=True)
    lname = Column(String, nullable=True)
    tg_id = Column(BigInteger, nullable=False)
    register_date = Column(DateTime, default=datetime.now, nullable=False)
    courses = relationship("Course", secondary="user_course", back_populates="users")

    def __repr__(self):
        return self.tg_id


class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    description_full = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    course_url = Column(String(250), nullable=False)
    users = relationship("User", secondary="user_course", back_populates="courses")

    def __repr__(self):
        return self.name
