from cl.cl import celery
import redis

import fedoraManager2.jobs as jobs

# local dependecies
import time
import sys


@celery.task()
def celeryTaskFactory(**kwargs):
	username = kwargs['username']

	# get selectedPIDs	
	userPag = jobs.userPagGen(username)	
	print "Found {count} PIDs for {username}".format(count=userPag.count,username=username)
	print "Paginator is",sys.getsizeof(userPag),"bytes"
	print "You have {PID_count} PIDs, will need {page_count} pages.".format(PID_count=userPag.count,page_count=userPag.num_pages)

	# run task by iterating through userPag (Paginator object)
	step = 1
	while step < userPag.count:
		kwargs['task_package']['count'] = step
		print "Firing off celery task",step
		
		####################################################################################################
		# HOW TO RUN FUNCTION FROM THIS FILE, WITH .delay() USING IT AS A KEYWORD?  IS THAT POSSIBLE?  
		####################################################################################################

		# need this to work...
		# result = funcHandle(kwargs['task_package']).delay()
		result = kwargs['task_function'].delay(kwargs['task_package'])
		# works, but not really possible
		# result = quickAddFactory.delay()

		# push to jobHand
		# task_package['jobHand'].assigned_tasks.append(str(result))		

		step += 1


@celery.task()
def quickAdd(jobStatusHand,a,b,count):

	# push to jobHand obj
	# jobStatusHand.assigned_tasks.append(count) #added

	print "Starting quickAdd:",count		
	
	jobStatusHand.completed_tasks.append(count) #added	

	# update job	
	jobs.jobStatusUpdate(jobStatusHand) #added

	# and kick it out
	time.sleep(.5)
	return a + b

@celery.task()
def quickAddFactory(task_package):	

	print "Starting quickAdd:",task_package['count']


	print task_package['jobStatusHand']

	
	task_package['jobStatusHand'].completed_tasks.append(task_package['count']) #added	

	# update job	
	jobs.jobStatusUpdate(task_package['jobStatusHand']) #added

	# and kick it out
	time.sleep(.5)
	return task_package['a'] + task_package['b']

