from datetime import datetime, timedelta
import time

def toMsEpoch(date):
	tt = datetime.timetuple(date)
	sec_epoch_loc = int(time.mktime(tt) * 1000)
	return sec_epoch_loc

def fromMsEpoch(ms):
	s = ms / 1000.0
	date = datetime.fromtimestamp(s)
	return date