from datetime import datetime
import time
while True:
    with open("/data/logs/app.log", "a") as f:
        f.write(f"{datetime.now()} - App is running\n")
    time.sleep(5)
