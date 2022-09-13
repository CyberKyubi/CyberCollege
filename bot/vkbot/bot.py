import asyncio
import logging
from typing import Optional, Union

from .api import VkAPI, make_request
from .timetable import Timetable
from utils.json_models.error import ErrorModel
from utils.json_models.doc_attachment import AttachmentModel
from storages.redis.storage import RedisStorage


class VkBot:
    def __init__(self, access_token: str, owner_id: int, redis: RedisStorage, excel_file: str):
        self.access_token: str = access_token
        self.owner_id: int = owner_id
        self.redis = redis
        self.excel_file = excel_file

        self.api = VkAPI()

        self.current_timetable_id: Optional[int] = None

    async def get_current_timetable(self):
        current_timetable_id = await self.redis.get_data('current_timetable_id')
        self.current_timetable_id = current_timetable_id

    async def set_current_timetable(self, current_timetable_id: int):
        await self.redis.set_data('current_timetable_id', current_timetable_id)
        self.current_timetable_id = current_timetable_id

    async def get_updates(self):
        await self.set_current_timetable(646407240)
        updates = await self.request()
        if updates:
            attachment_model = AttachmentModel(**updates[0]['doc'])
            logging.info(f'New timetable [{attachment_model.title}] timetable id [{attachment_model.id}]')
            await self.set_current_timetable(attachment_model.id)

            done, pending = await asyncio.wait([self.download_excel_file(attachment_model.url)])
            if done:
                timetable = Timetable(self.excel_file).prepare_dataframe()

        else:
            logging.info('No updates')

    async def request(self) -> Union[None | list[dict]]:
        url = self.api.api_url(self.owner_id, self.access_token)

        response, _ = await make_request(url)
        if isinstance(response, ErrorModel):
            logging.error(f'status code [{response.status_code}] | error code [{response.error_code}] '
                          f'| error message [{response.error_msg}]')
            return

        await self.get_current_timetable()

        for item in response['response']['items']:
            attachments = item.get('attachments')
            if attachments:
                doc_attachment = list(filter(self.filter_attachments, attachments))
                new_timetable = list(filter(self.filter_timetable, doc_attachment))
                if new_timetable:
                    return new_timetable

    @staticmethod
    def filter_attachments(attachment: dict) -> dict:
        if attachment['type'] == 'doc' and 'Курчатова.xls' in attachment['doc']['title']:
            return attachment

    def filter_timetable(self, timetable: dict) -> dict:
        if timetable['doc']['id'] > self.current_timetable_id:
            return timetable

    async def download_excel_file(self, url: str):
        _, content = await make_request(url, download=True)
        with open(self.excel_file, 'wb') as file:
            file.write(content)
