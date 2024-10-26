from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(256))

# Define the Articles table
class Article(Base):
    __tablename__ = 'articles'
    
    article_id = Column(Integer, primary_key=True, autoincrement=True) # Primary Key, independed from arxiv id
    arxiv_id = Column(String, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    ai_summary = Column(Text)
    published = Column(TIMESTAMP)
    updated = Column(TIMESTAMP)
    # doi = Column(String)
    pdf_link = Column(String)
    html_link = Column(String)
    primary_category = Column(String)
    # total_results = Column(Integer)
    # search_query = Column(Text)
    favorites = Column(Integer) # Favorite of the user

# Create the SQLite database
DATABASE_URI = 'sqlite:///hci_database.sqlite3'
engine = create_engine(DATABASE_URI)

# Create all tables
Base.metadata.create_all(engine)

print("\nDatabase 'hci_database.sqlite3' created successfully with all tables.\n")