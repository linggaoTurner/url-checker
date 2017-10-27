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
    health = ''
    status = ''
    try:
        r = requests.get(url, timeout=6)
        status = r.status_code

        if urlInventory.select(urlInventory.expectedStatus).where(urlInventory.urlDomain == url) == status and urlInventory.select(urlInventory.expectedString).where(urlInventory.urlDomain == url) == r.text:
            health = 'SUCCESS'
        else:
            health = 'FAILURE'
    except requests.exceptions.InvalidSchema as e:
        print("Invalid Schema")
        health = 'FAILURE'
        storeLogs(url,status,health)
    except requests.exceptions.ReadTimeout as e:
        print("Time Out")
        health = 'FAILURE'
        storeLogs(url,status,health)
        except requests.exceptions.ConnectionError as e:
        print("Connection Issue")
        health = 'FAILURE'
        storeLogs(url,status,health)
    except requests.exceptions.TooManyRedirects as e:
        print("Too Many Redirects")
        health = 'FAILURE'
        storeLogs(url,status,health)
    except requests.exceptions.ChunkedEncodingError as e:
        print("Encoding Error")
        health = 'FAILURE'
        storeLogs(url,status,health)

    healthlist = []
    for data in urlLog.select().order_by(urlLog.id.desc()).limit(3):
        healthlist.append(data.healthyState)
    if healthlist.count('FAILURE') == 3:
        sendEmail.sent(url)

def storeLogs(url,status,health):
    urlLog.create(urlDomain = url,
                  timeChecked=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  statusCode=status,
                  healthyState=health)
