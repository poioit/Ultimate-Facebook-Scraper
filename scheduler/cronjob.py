from datetime import datetime, timedelta  # for Scheduler
import time
from croniter import croniter
import os
# Class for Scheduling


class schedule_fun():
    def starter(self):
        nextRunTime = self.getNextCronRunTime(schedule)
        while True:
            roundedDownTime = self.roundDownTime()
            if (roundedDownTime == nextRunTime):
                global timestamp
                timestamp = datetime.now().strftime("%B %d %Y, %H:%M:%S")
                # For setting variables with values
                print("run scraper")
                # absolute path
                cur_dir = os.getcwd()
                os.system('python ' + cur_dir +
                          '/scraper/scraper.py --total_scrolls ' + scroll)
                nextRunTime = self.getNextCronRunTime(schedule)
            elif (roundedDownTime > nextRunTime):
                print("error")

                # We missed an execution. Error. Re initialize.
                nextRunTime = self.getNextCronRunTime(schedule)
            self.sleepTillTopOfNextMinute()
    # Round time down to the top of the previous minute

    def roundDownTime(self, dt=None, dateDelta=timedelta(minutes=1)):
        roundTo = dateDelta.total_seconds()
        if dt == None:
            dt = datetime.now()
        seconds = (dt - dt.min).seconds
        rounding = (seconds+roundTo/2) // roundTo * roundTo
        return dt + timedelta(0, rounding-seconds, -dt.microsecond)
    # Get next run time from now, based on schedule specified by cron string

    def getNextCronRunTime(self, schedule):
        return croniter(schedule, datetime.now()).get_next(datetime)
    # Sleep till the top of the next minute

    def sleepTillTopOfNextMinute(self):
        t = datetime.utcnow()
        sleeptime = 60 - (t.second + t.microsecond/1000000.0)
        time.sleep(sleeptime)


# trigger every 2 hours
schedule = '* */2 * * *'
# args
scroll = '3'
scl = schedule_fun()
scl.starter()
