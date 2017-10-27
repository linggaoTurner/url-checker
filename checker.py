import requests
from models import urlInventory,urlLog
import datetime
import sys
import os
import sendEmail
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()
sched.start()

#set up scheduler at intervals
def urlchecker(url,frequency):
    sched.add_job(schedulejob,'interval',[url], seconds = float(frequency))

def schedulejob(url):
    r = requests.get(url)
    health = ''

    if urlInventory.select(urlInventory.expectedStatus).where(urlInventory.urlDomain == url) == r.status_code and urlInventory.select(urlInventory.expectedString).where(urlInventory.urlDomain == url) == r.text:
        health = 'SUCCESS'
    else:
        health = 'FAILURE'

    urlLog.create(urlDomain = url,
                   timeChecked=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                   statusCode=r.status_code,
                   healthyState=health)
    healthlist = []
    for data in urlLog.select().order_by(urlLog.id.desc()).limit(3):
        healthlist.append(data.healthyState)
    if healthlist.count('FAILURE') == 3:
        sendEmail.sent(url)
