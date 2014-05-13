from cl.cl import celery
import redis

import fedoraManager2.jobs as jobs

# local dependecies
import time
import sys


@celery.task()
def celeryTaskFactory(**kwargs):
	
	# create job_package
	job_package = kwargs['job_package']

	# get selectedPIDs	
	userPag = jobs.userPagGen(job_package['username'])	
	print "Found {count} PIDs for {username}".format(count=userPag.count,username=job_package['username'])	

	# run task by iterating through userPag (Paginator object)
	step = 1
	while step < userPag.count:
		job_package['step'] = step
		print "Firing off task:",step		
		# result = kwargs['task_function'].delay(kwargs['job_package'])				
		result = kwargs['task_function'].delay(job_package)				
		step += 1


@celery.task()
def taskv3(job_package):

	username = job_package['username']
	print "Starting taskv3",job_package['step']		

	# delay
	time.sleep(.25)
	
	# return results
	return 40 + 2	


# @celery.task()
# def quickAdd(jobStatusHand,a,b,count):

# 	# push to jobHand obj
# 	# jobStatusHand.assigned_tasks.append(count) #added

# 	print "Starting quickAdd:",count		
	
# 	jobStatusHand.completed_tasks.append(count) #added	

# 	# update job	
# 	jobs.jobStatusUpdate(jobStatusHand) #added

# 	# and kick it out
# 	time.sleep(.5)
# 	return a + b

# @celery.task()
# def quickAddFactory(**kwargs):
# 	username = kwargs['username']

# 	# get selectedPIDs	
# 	userPag = jobs.userPagGen(username)	
# 	print "Found {count} PIDs for {username}".format(count=userPag.count,username=username)
# 	print "You have {PID_count} PIDs, will need {page_count} pages.".format(PID_count=userPag.count,page_count=userPag.num_pages)

# 	# run task by iterating through userPag (Paginator object)
# 	step = 1
# 	while step < userPag.count:
# 		kwargs['task_package']['count'] = step
# 		print "Starting quickAdd:",kwargs['task_package']['count']
# 		print kwargs['task_package']['jobStatusHand']	
# 		kwargs['task_package']['jobStatusHand'].completed_tasks.append(kwargs['task_package']['count']) #added	
# 		# update job	
# 		jobs.jobStatusUpdate(kwargs['task_package']['jobStatusHand']) #added
# 		print "update successful"
# 		# and kick it out
# 		# time.sleep(.5)
# 		step += 1	


		

















