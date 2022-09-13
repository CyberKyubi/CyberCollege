from sqlalchemy import Column, Integer, BigInteger, VARCHAR

from .base import Base


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    tg_user_id = Column(BigInteger)
    college_group = Column(VARCHAR(length=10))
