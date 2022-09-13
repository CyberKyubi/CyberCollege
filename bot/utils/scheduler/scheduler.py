from apscheduler.schedulers.asyncio import AsyncIOScheduler


class GetUpdatesFromVk:
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler

    def start_job(self, func):
        self.scheduler.add_job(func, trigger='cron', second='*/5', timezone='Europe/Samara')
