import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sys
import appSettings
import models
#sending email with livestream links
def searchUrls():
    dataset = []
    logData = models.urlLog
    if logData.select().count() > 0:
        for data in logData.select(logData.urlDomain)
                                 .group_by()
            dataDict = {}
            dataDict['title'] = data.title
            dataDict['link'] = data.link
            dataset.append(dataDict)
        q = models.Requests.update(reported = 1).where(models.Requests.livestream == 1)
        q.execute()
    sent(dataset)

def sent(content):

    msg = MIMEMultipart()
    fromme = "Ling.Gao@turner.com"
    mails = ['Ling.Gao@turner.com','Joe.Green@turner.com']
    msg['From'] = fromme
    msg['To'] = ",".join(mails)
    msg['Subject'] = "URL checker"
    b1 = 'Hi ,\n\nThe following URL is not healthy:\n\n'
    b3 = '\n\nRegards,\n\nLing Gao'
    b2 = content[0] + ": \n" + content[1] + ",\n\n"
    print(b2)
    body = b1 + b2 + b3
    msg.attach(MIMEText(body))


    try:
        # below the configuration is only for AWS EC2 sent SMTP only
        s = smtplib.SMTP(appSettings.SMTPserver, appSettings.SMTPport)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.set_debuglevel(True)
        s.login(appSettings.SMTPUsername, appSettings.SMTPPassword)
        s.sendmail(fromme, mails, msg.as_string())
        s.quit()

    except smtplib.SMTPServerDisconnected:
        print ("smtplib.SMTPServerDisconnected")
    except smtplib.SMTPResponseException as e:
        print ("smtplib.SMTPResponseException: " + str(e.smtp_code) + " " + str(e.smtp_error))
    except smtplib.SMTPSenderRefused:
        print ("smtplib.SMTPSenderRefused")
    except smtplib.SMTPRecipientsRefused:
        print ("smtplib.SMTPRecipientsRefused")
    except smtplib.SMTPDataError:
        print ("smtplib.SMTPDataError")
    except smtplib.SMTPConnectError:
        print ("smtplib.SMTPConnectError")
    except smtplib.SMTPHeloError:
        print ("smtplib.SMTPHeloError")
    except smtplib.SMTPAuthenticationError:
        print ("smtplib.SMTPAuthenticationError")

    return

if __name__ == '__main__':
    searchLivestream()
