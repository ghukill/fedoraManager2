from cl.cl import celery


import time

@celery.task()
def add_together(a, b, count):
	print "Starting:",count
	time.sleep(.1)
	return a + b