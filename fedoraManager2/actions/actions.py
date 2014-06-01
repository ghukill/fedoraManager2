from cl.cl import celery
import redis

import fedoraManager2.jobs as jobs
import fedoraManager2.redisHandles as redisHandles
import fedoraManager2.models as models

# local dependecies
import time
import sys




@celery.task()
def celeryTaskFactory(**kwargs):
	
	# create job_package
	job_package = kwargs['job_package']
	print job_package['jobHand'].assigned_tasks

	# get username
	username = job_package['username']

	# get and iterate through user selectedPIDs
	# NO PAGINATION				
	PIDlist = kwargs['PIDlist']	
	
	step = 1		
		
	# iterate through PIDs in userPID_pag page
	for PID in PIDlist:			
		# print "Operating on PID:",PID," / Step:",step		
		job_package['step'] = step			
		# fire off async task		
		result = kwargs['task_function'].delay(job_package)				
		# push result to jobHand
		job_package['jobHand'].assigned_tasks.append(result)
		# updates jobHand in redis so that polling process get up-to-date reflection of tasks added
		jobs.jobUpdate(job_package['jobHand'])
		step += 1

	print "Finished assigning tasks"

@celery.task()
def sampleTask(job_package):

	username = job_package['username']
	# print "Starting sampleTask",job_package['step']
	
	# delay for testing	
	# because tasks are launched async, this pause will affect the task, but will not compound for all tasks
	time.sleep(5)	
	
	# update taskHand about task	
	redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "triggered")	

	# return results
	return 40 + 2


@celery.task()
def sampleFastTask(job_package):

	username = job_package['username']
	# print "Starting sampleFastTask",job_package['step']
	
	# delay for testing	
	# time.sleep(.25)	
	
	# update taskHand about task	
	redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "triggered")	

	# return results
	return 40 + 2






		

















