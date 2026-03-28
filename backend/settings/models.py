from sqlalchemy import Column, Integer, String
from database import Base

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    theme = Column(String, default="dark")