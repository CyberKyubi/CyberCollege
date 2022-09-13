from pydantic import BaseModel


class AttachmentModel(BaseModel):
    id: int
    owner_id: int
    title: str
    size: int
    ext: str
    date: int
    type: int
    url: str
    access_key: str
