from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from .models import Base, User, Course
from config_data.config import load_config, Config

POOL_SIZE = 20
MAX_OVERFLOW = 0

config: Config = load_config()

database_url = f'postgresql://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:5432/{config.db.database}'

engine = create_engine(database_url, echo=False, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def add_user(tg_id, fname, lname):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    if user is None:
        new_user = User(tg_id=tg_id, fname=fname, lname=lname)
        session.add(new_user)
        session.commit()
        return True
    return False


def get_user_id(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    return user.id


def get_course(course_id):
    session = Session()
    course = session.query(Course).filter(Course.id == course_id).first()
    return course


def get_user_courses(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    courses = user.courses
    return courses


def add_course(tg_id, course_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    course = session.query(Course).filter(Course.id == course_id).first()
    user.courses.append(course)
    session.add(user)
    session.commit()


def get_all_courses(tg_id):
    session = Session()
    user = session.query(User).filter(User.tg_id == tg_id).first()
    user_courses = user.courses
    user_courses = [course_id.id for course_id in user_courses]
    remaining_courses = session.query(Course).filter(Course.id.notin_(user_courses))
    return remaining_courses