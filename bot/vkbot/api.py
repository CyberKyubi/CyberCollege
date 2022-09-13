import logging
import certifi
import ssl
from typing import Optional, Type, Union
from http import HTTPStatus

import aiohttp

from utils.json_models.error import ErrorModel


class VkAPI:
    def __init__(self):
        self.method = 'wall.get'
        self.v = '5.131'
        self.offset = 1
        self.count = 7

    def api_url(self, owner_id: int, access_token: str):
        url = 'https://api.vk.com/method/{method}' \
              '?owner_id={owner_id}&v={v}&offset={offset}&count={count}&access_token={access_token}'
        return url.format(
            method=self.method,
            owner_id=owner_id,
            v=self.v,
            offset=self.offset,
            count=self.count,
            access_token=access_token
        )


class Session:
    def __init__(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        self._session: Optional[aiohttp.ClientSession] = None
        self._connector_class: Type[aiohttp.TCPConnector] = aiohttp.TCPConnector
        self._connector_init = dict(ssl=ssl_context)

    async def __aenter__(self) -> aiohttp.ClientSession:
        self._session = aiohttp.ClientSession(connector=self._connector_class(**self._connector_init))
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()


async def check_result(
        status_code: int,
        response_data: Optional[dict] = None,
        response_content: Optional[bytes] = None
) -> Union[tuple[dict, bytes] | ErrorModel]:
    if HTTPStatus.OK <= status_code <= HTTPStatus.IM_USED:
        return response_data, response_content
    elif status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND):
        return ErrorModel(status_code=status_code, **response_data['error'])


async def make_request(url: str, download=False) -> Union[tuple[dict, bytes] | ErrorModel]:
    try:
        async with Session() as session:
            async with session.get(url) as response:
                if download:
                    return await check_result(response.status, response_content=await response.read())
                else:
                    return await check_result(response.status, response_data=await response.json())
    except aiohttp.ClientError as e:
        logging.error(f"aiohttp client throws an error: {e.__class__.__name__}: {e}")