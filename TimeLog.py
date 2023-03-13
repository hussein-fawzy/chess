from datetime import datetime

logs = {}


class ChannelExists(Exception):
    pass

class ChannelDoesNotExist(Exception):
    pass

class SampleNotStarted(Exception):
    pass


def add_channel(name):
	if name in logs:
		raise ChannelExists("There is already a channel with the same name.")

	logs[name] = {'count': 0, 'sum': 0.0, 'min': -1, 'max': -1, 'start_time': 0}

def remove_channel(name):
	try:
		del logs[name]
	except KeyError:
		raise ChannelDoesNotExist("There is not channel with this name.")

def remove_all():
	logs.clear()

def reset_channel(name):
	try:
		logs[name]['count'] = 0
		logs[name]['sum'] = 0.0
		logs[name]['min'] = -1
		logs[name]['max'] = -1
		logs[name]['start_time'] = 0
	except KeyError:
		raise ChannelDoesNotExist("There is not channel with this name.")

def reset_all():
	for ch in logs:
		reset_channel(ch)


#start an automatic sample log
def start_sample(channel):
	try:
		logs[channel]['start_time'] = datetime.now()
	except KeyError:
		raise ChannelDoesNotExist("There is not channel with this name.")

#end and log the started automatic sample log
def end_sample(channel):
	try:
		if logs[channel]['start_time'] == 0:
			raise SampleNotStarted("There is no sample in measurement for this channel.")

		length = datetime.now() - logs[channel]['start_time']
		log(channel, length.seconds * 1000000 + length.microseconds)

		logs[channel]['start_time'] = 0
	except KeyError:
		raise ChannelDoesNotExist("There is not channel with this name.")

#stop and cancel an automatic sample log
def stop_sample(channel):
	try:
		logs[channel]['start_time'] = 0
	except KeyError:
		raise ChannelDoesNotExist("There is not channel with this name.")

#manually log a sample (value is in microseconds)
def log(channel, value):
	try:
		logs[channel]['count'] += 1
		logs[channel]['sum'] += value

		if value > logs[channel]['max']:
			logs[channel]['max'] = value
		elif value < logs[channel]['min'] or logs[channel]['min'] == -1:
			logs[channel]['min'] = value
	except KeyError:
		raise ChannelDoesNotExist("There is not channel with this name.")


def print_stats(channel):
	try:
		print("Stats for:", channel)

		if logs[channel]['count'] == 0:
			print("Channel is empty")
		else:
			print("N:", logs[channel]['count'], "- SUM:", logs[channel]['sum'], "- MIN:", logs[channel]['min'], "- AVG:", int(logs[channel]['sum'] / logs[channel]['count']), "- MAX:", logs[channel]['max'])
		
		print("")
	except KeyError:
		raise ChannelDoesNotExist("There is no channel with this name.")

def print_all():
	for ch in logs:
		print_stats(ch)
