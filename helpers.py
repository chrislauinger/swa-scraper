from datetime import datetime, timedelta
import time

import smtplib
import email.utils
from email.mime.text import MIMEText

from privateConstants import * 

def toMsEpoch(date):
	tt = datetime.timetuple(date)
	sec_epoch_loc = int(time.mktime(tt) * 1000)
	return sec_epoch_loc

def fromMsEpoch(ms):
	s = ms / 1000.0
	date = datetime.fromtimestamp(s)
	return date

def costString(cost, usingPoints):
	return "%s%s %s" % ("$" if not usingPoints else "", cost, "points" if usingPoints else "")



def sendEmail(to, subject, message):

	msg = MIMEText(message)
	msg['To'] = email.utils.formataddr(('Recipient', to))
	msg['From'] = email.utils.formataddr(('Dragon', author))
	msg['Subject'] = subject

	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(author, password)
		server.sendmail(author, to, msg.as_string())
		server.close()
		print 'successfully sent the mail'
	except Exception as e:
		print 'fail to send mail'
