from sqlalchemy import Column, Integer, BigInteger, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class CollegeGroups(Base):
    __tablename__ = 'college_groups'

    id = Column(Integer)
    college_group = Column(VARCHAR(length=11), primary_key=True)
    college_building = Column(VARCHAR(length=20))

    children = relationship('Users')


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    college_group = Column(VARCHAR(length=11), ForeignKey('college_groups.college_group'))
    college_building = Column(VARCHAR(length=20))
