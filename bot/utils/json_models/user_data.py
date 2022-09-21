from typing import Optional, List

from pydantic import BaseModel


class GroupInfoModel(BaseModel):
    college_building: str
    group: str


class UserModel(BaseModel):
    current_group: GroupInfoModel
    default_college_group: str
    default_college_building: str
    groups_friends: Optional[List[GroupInfoModel]] = None
    selected_timetable: Optional[str] = None
    group_added: Optional[str] = ''
