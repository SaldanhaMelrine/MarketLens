import schedule
import time
from update_job import run_update

def job():
    print("Running scheduled update...")
    run_update()

# run every 1 minute
schedule.every(1).minutes.do(job)

print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(1)