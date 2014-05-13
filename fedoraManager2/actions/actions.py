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

	# EXPLORATION
	print "###########################################################################################################################"
	# print job_package['jobHand']
	# print job_package['jobHand'].estimated_tasks
	print "###########################################################################################################################"

	# run task by iterating through userPag (Paginator object)
	step = 1
	while step < (userPag.count + 1):
		job_package['step'] = step
		print "Firing off task:",step				
		result = kwargs['task_function'].delay(job_package)				

		# push result to jobHand
		job_package['jobHand'].assigned_tasks.append(result)
		jobs.jobUpdate(job_package['jobHand'])

		step += 1


@celery.task()
def sampleTask(job_package):

	username = job_package['username']
	print "Starting sampleTask",job_package['step']		

	# delay
	time.sleep(.25)
	
	# push to completed tasks in taskHand
	job_package['taskHand'].last_completed_task_num = job_package['step']
	jobs.taskUpdate(job_package['taskHand'])

	# return results
	return 40 + 2	



		

















