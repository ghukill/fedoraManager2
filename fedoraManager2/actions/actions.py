from cl.cl import celery
import redis

import fedoraManager2.jobs as jobs

# local dependecies
import time



@celery.task()
def quickAdd(job_num,a, b, count):
	'''
	maybe get jobStatusHand from redis here, then update...
	'''
	# get job	
	jobHand = jobs.jobGet(job_num)['jobHand']
	jobStatusHand = jobs.jobGet(job_num)['jobStatusHand']

	# push to jobHand obj
	jobStatusHand.assigned_tasks.append(count) #added

	print "Starting quickAdd:",count	

	# update jobStatusHand
	jobStatusHand.completed_tasks.append(count) #added	

	# update job	
	jobs.jobStatusUpdate(jobStatusHand) #added

	# and kick it out
	return a + b


# @celery.task()
# def longAdd(a, b, count):
# 	print "Starting longAdd:",count	
# 	time.sleep(.25)
# 	return a + b