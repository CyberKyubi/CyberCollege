from storages.redis.storage import RedisStorage


async def set_current_role(owner_id: str, role: str, redis__db_1: RedisStorage):
    owners_data = await redis__db_1.get_data('owners')
    owner = owners_data.get(owner_id, {})
    owner.update(role=role)
    owners_data[owner_id] = owner
    await redis__db_1.set_data('owners', owners_data)