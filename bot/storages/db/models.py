from sqlalchemy import Column, Integer, BigInteger, VARCHAR, ForeignKey, Sequence
from sqlalchemy.orm import relationship

from .base import Base


class CollegeGroups(Base):
    __tablename__ = 'college_groups'

    id = Column(Integer, Sequence('college_groups_id_seq', start=1, increment=1))
    college_group = Column(VARCHAR(length=11), primary_key=True)
    college_building = Column(VARCHAR(length=20))

    children = relationship('Users')


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('users_id_seq', start=1, increment=1), primary_key=True)
    user_id = Column(BigInteger)
    college_group = Column(
        VARCHAR(length=11), ForeignKey('college_groups.college_group', ondelete='CASCADE', onupdate='CASCADE')
    )
    college_building = Column(VARCHAR(length=20))
    role = Column(VARCHAR(length=7), default='student')
