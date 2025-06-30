import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import message_router

if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))
    scheduler.add_job(
        message_router.send_system_news_update_to_all_users,
        CronTrigger(hour=9, minute=0),
        id='morning_news_update',
        replace_existing=True
    )
    scheduler.add_job(
        message_router.send_system_news_update_to_all_users,
        CronTrigger(hour=21, minute=36),
        id='evening_news_update',
        replace_existing=True
    )
    scheduler.start()
    print('Scheduler started. Press Ctrl+C to exit.')
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print('Scheduler stopped.') 