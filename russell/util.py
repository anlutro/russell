import datetime
import time


def generate_excerpt(body):
	excerpt_parts = []
	for line in body.splitlines():
		if line == '':
			break
		excerpt_parts.append(line)
	return ' '.join(excerpt_parts)


def now_datetime_str(utc=False, include_timezone=True):
	if utc:
		now = datetime.datetime.utcnow()
	else:
		now = datetime.datetime.now()

	ret = now.strftime('%Y-%m-%d %H:%M:%S')

	if include_timezone:
		if utc:
			now = time.gmtime()
		else:
			now = time.localtime()
		ret += ' ' + time.strftime('%z', now)

	return ret


def parse_pubdate(pubdate):
	formats = ('%Y-%m-%d %H:%M:%S %z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d')
	for dateformat in formats:
		try:
			return datetime.datetime.strptime(pubdate, dateformat)
		except ValueError:
			pass
	return None
