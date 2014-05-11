from cl.cl import celery
import redis

import fedoraManager2.jobs as jobs

# local dependecies
import time



@celery.task()
def quickAdd(jobStatusHand,a, b, count):

	'''
	an interesting async problem - when hitting redis, missing a beat here and there...
	'''

	# push to jobHand obj
	# jobStatusHand.assigned_tasks.append(count) #added

	print "Starting quickAdd:",count	

	# update jobStatusHand
	jobStatusHand.completed_tasks.append(count) #added	

	# update job	
	jobs.jobStatusUpdate(jobStatusHand) #added

	# and kick it out
	time.sleep(.5)
	return a + b


# @celery.task()
# def longAdd(a, b, count):
# 	print "Starting longAdd:",count	
# 	time.sleep(.25)
# 	return a + b