from cl.cl import celery
from celery import Task
import redis

import fedoraManager2.jobs as jobs
import fedoraManager2.redisHandles as redisHandles
import fedoraManager2.models as models

# local dependecies
import time
import sys


class DebugTask(Task):
	abstract = True
	def after_return(self, *args, **kwargs):

		# print args
		print args
		status = args[0]
		task_id = args[2]
		task_details = args[3]
		step = task_details[0]['step']
		job_num = task_details[0]['job_num']

		redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=step,job_num=job_num), status)
		# print('Task returned: {0!r}'.format(self.request))


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

@celery.task(base=DebugTask)
def sampleTask(job_package):

	username = job_package['username']	
	
	# delay for testing	
	# because tasks are launched async, this pause will affect the task, but will not compound for all tasks	
	time.sleep(5)	
	
	# update about task	
	redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "fired")	
	
	# increments completed tasks
	jobs.jobUpdateCompletedCount(job_package['job_num'])

	# return results
	return 40 + 2


@celery.task(base=DebugTask)
def sampleFastTask(job_package):

	username = job_package['username']		
	
	# update about task	
	redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "fired")	
	
	# increments completed tasks
	jobs.jobUpdateCompletedCount(job_package['job_num'])

	# return results
	return 40 + 2



