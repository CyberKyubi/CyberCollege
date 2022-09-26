import logging

from storages.redis.storage import RedisStorage


async def set_current_role(owner_id: str, role: str, redis__db_1: RedisStorage):
    """
    Записывает текущую роль в redis.
    :param owner_id:
    :param role:
    :param redis__db_1:
    :return:
    """
    owners_data = await redis__db_1.get_data('owners')
    owner = owners_data.get(owner_id, {})
    owner.update(role=role)
    owners_data[owner_id] = owner
    logging.info(f"Owner [{owner_id}] сменил роль на [{role} role]")
    await redis__db_1.set_data('owners', owners_data)