import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from storages.redis.storage import RedisStorage


class DeleteOldTimetable:
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    @staticmethod
    async def delete_old_timetable(redis__db_2: RedisStorage):
        """
        Удаляет старое расписание.
        :param redis__db_2:
        :return:
        """
        logging.debug(f'BOT | Действие | удаление [Старое расписание]')
        new_timetable = await redis__db_2.get_data('timetable_for_new_week')
        await redis__db_2.delete_key('timetable_for_new_week')
        if new_timetable:
            await redis__db_2.set_data('timetable', new_timetable)
        else:
            old_timetable = await redis__db_2.get_data('timetable')
            if old_timetable:
                await redis__db_2.delete_key('timetable')

    async def start_job(self, redis__db_2):
        self.scheduler.add_job(
            self.delete_old_timetable,
            trigger='cron',
            day_of_week='sun',
            hour=0,
            minute=0,
            timezone='Europe/Samara',
            args=(redis__db_2, )
        )
