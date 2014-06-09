from cl.cl import celery
from celery import Task
import redis

import fedoraManager2.jobs as jobs
import fedoraManager2.redisHandles as redisHandles
import fedoraManager2.models as models

# local dependecies
import time
import sys


# Class that updates task status in redis *after* task is complete
'''
PID locking: this could "unlock" the PID from SQL table
'''
class postTask(Task):
	abstract = True
	def after_return(self, *args, **kwargs):

		# extract task data		
		status = args[0]
		task_id = args[2]
		task_details = args[3]
		step = task_details[0]['step']
		job_num = task_details[0]['job_num']

		# debug printing
		# print "TASK DETAILS:","status:",status," / task_id:",task_id," / task details:",task_details,"/ step:",step," / job number:",job_num

		# update job with task completion				
		redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=step,job_num=job_num), status)	
	
		# increments completed tasks
		jobs.jobUpdateCompletedCount(job_num)

		# save task status in redis
		redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=step,job_num=job_num), status)		
		


@celery.task()
def celeryTaskFactory(**kwargs):
	
	# create job_package
	job_package = kwargs['job_package']
	print job_package['jobHand'].assigned_tasks

	# get username
	username = job_package['username']

	# get job_num
	job_num = kwargs['job_num']

	# get and iterate through user selectedPIDs			
	PIDlist = kwargs['PIDlist']	
	
	step = 1		
		
	# iterate through PIDs in userPID_pag page
	'''
	PID locking: check if PID locked in SQL table, otherwise lock
	'''
	for PID in PIDlist:			
		# print "Operating on PID:",PID," / Step:",step		
		job_package['step'] = step			
		# fire off async task		
		result = kwargs['task_function'].delay(job_package)		
		task_id = result.id
		redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "FIRED")
			
		# update incrementer for total assigned
		jobs.jobUpdateAssignedCount(job_num)

		# bump step
		step += 1

	print "Finished assigning tasks"

@celery.task(base=postTask)
def sampleTask(job_package):

	username = job_package['username']	
	
	'''
	This is where all the action for the task will take place.
	'''

	# delay for testing	
	# because tasks are launched async, this pause will affect the task, but will not compound for all tasks	
	time.sleep(5)	
	
	# return results
	return 40 + 2


@celery.task(base=postTask)
def sampleFastTask(job_package):

	username = job_package['username']

	# return results
	return 40 + 2



