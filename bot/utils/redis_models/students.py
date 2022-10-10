from typing import Dict

from pydantic import BaseModel


class StudentModel(BaseModel):
    user_id: str = ''


class GroupModel(BaseModel):
    group: str
    list_students: list
    selected_user: StudentModel = StudentModel()


class CachedGroupModel(BaseModel):
    list_students_msg: str
    students: Dict[str, str]