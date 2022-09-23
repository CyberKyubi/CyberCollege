from enum import Enum

from pydantic import BaseModel


class Roles(str, Enum):
    admin = 'Admin'
    user = 'User'
    owner = 'Owner'


class OwnerModel(BaseModel):
    role: Roles

    class Config:
        use_enum_values = True
