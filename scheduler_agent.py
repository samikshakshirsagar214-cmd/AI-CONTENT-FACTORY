import schedule
import time
from datetime import datetime
from src.manager.manager_agent import run_pipeline


def job():
    print("\n==============================")
    print("⏰ Running Scheduled Pipeline")
    print("🕒 Time:", datetime.now())
    print("==============================\n")

    run_pipeline()


# -----------------------------
# SCHEDULE SETTINGS
# -----------------------------

#Run twice daily
schedule.every().day.at("18:29").do(job)
schedule.every().day.at("21:00").do(job)

# Optional: test every 2 minutes (for debugging)
#schedule.every(2).minutes.do(job)


print("🚀 Scheduler Started...")
print("📅 Videos will be uploaded at 10:00 AM and 6:00 PM daily\n")


# -----------------------------
# LOOP
# -----------------------------
while True:
    print("Waiting for scheduled time..........")
    schedule.run_pending()
    time.sleep(30)