from sqlalchemy import create_engine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionSQL = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


while True:
    try:
        conn = psycopg2.connect(host=settings.database_hostname,
                                database=settings.database_name,
                                user=settings.database_username,
                                password=settings.database_password,
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        break
    except Exception as error:
        print('db connect fail')
        print('error', error)
        time.sleep(5)
