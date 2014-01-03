#-*- coding: UTF-8 -*-

import datetime
import time

def unixTimeStamp():
	return int(time.mktime(datetime.datetime.now().timetuple()))


def __test():
	print unixTimeStamp()

if __name__ == '__main__':
	__test()