from cl.cl import celery

# local dependecies
import time



@celery.task()
def quickAdd(a, b, count):
	print "Starting quickAdd:",count	
	return a + b


@celery.task()
def longAdd(a, b, count):
	print "Starting longAdd:",count	
	time.sleep(.25)
	return a + b