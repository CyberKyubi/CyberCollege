from pydantic import BaseModel


class TimetableChangesModel(BaseModel):
    number_of_college_building: int
    first_college_buildings: str = ''
    college_buildings_info: dict = {}
