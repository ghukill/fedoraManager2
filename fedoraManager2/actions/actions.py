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
		PID = task_details[0]['PID']

		# release PID from PIDlock
		redisHandles.r_PIDlock.delete(PID)

		# debug printing
		# print "TASK DETAILS:","status:",status," / task_id:",task_id," / task details:",task_details,"/ step:",step," / job number:",job_num

		# update job with task completion				
		redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=step,job_num=job_num), status)	
	
		# increments completed tasks
		jobs.jobUpdateCompletedCount(job_num)		


def lockCheck(job_package):
	# check PIDlock
	lock_status = redisHandles.r_PIDlock.exists(job_package['PID'])
	# if locked, divert
	if lock_status == True:
		# update job with task completion				
		redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "LOCKED")	
	
		# DON'T increment completed tasks
		# jobs.jobUpdateCompletedCount(job_num)	

		raise Exception('PID locked, skipping...');
	else:
		redisHandles.r_PIDlock.set(job_package['PID'],1)



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
		
	# iterate through PIDs 	
	for PID in PIDlist:		

		# OLD, WORKING
		# print "Operating on PID:",PID," / Step:",step		
		job_package['step'] = step	
		job_package['PID'] = PID		
		# fire off async task		
		result = kwargs['task_function'].delay(job_package)		
		task_id = result.id
		redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "FIRED")
			
		# update incrementer for total assigned
		jobs.jobUpdateAssignedCount(job_num)

		# bump step
		step += 1	
		
		#NEW, NO WORKING
		# # check PIDlock, set if not
		# lock_status = redisHandles.r_PIDlock.exists(PID)

		# # unlocked
		# if lock_status == False:
		# 	redisHandles.r_PIDlock.set(PID,1)

		# 	# print "Operating on PID:",PID," / Step:",step		
		# 	job_package['step'] = step	
		# 	job_package['PID'] = PID		
		# 	# fire off async task		
		# 	result = kwargs['task_function'].delay(job_package)		
		# 	task_id = result.id
		# 	redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "FIRED")
				
		# 	# update incrementer for total assigned
		# 	jobs.jobUpdateAssignedCount(job_num)

		# 	# bump step
		# 	step += 1

		# # locked
		# else:
		# 	'''
		# 	cannot poll with "while", holds up celery workers and eventually gums everything up
		# 	alternate option - fail, but save the PID!			
		# 	'''
		# 	

	print "Finished assigning tasks"



@celery.task(base=postTask,bind=True)
def sampleTask(self,job_package,*args, **kwargs):
	try:
		lockCheck(job_package)
	except:
		time.sleep(.25)
		raise self.retry(countdown=2)

	# task
	username = job_package['username']

	# delay for testing		
	time.sleep(2)	
	
	# return results
	return 40 + 2


@celery.task(base=postTask,bind=True)
def sampleFastTask(self,job_package,*args, **kwargs):
	try:
		lockCheck(job_package)
	except:
		time.sleep(.25)
		raise self.retry(countdown=2)

	username = job_package['username']

	# return results
	return 40 + 2



@celery.task(base=postTask)
def writeTest(job_package):
	lockCheck(job_package)

	username = job_package['username']
	filename = "test_file.txt"
	fhand = open(filename,'a')
	print "********* FILE OPEN {step} **************".format(step=job_package['step'])
	time.sleep(.25)
	fhand.write("The step is: {step}\n".format(step=job_package['step']))
	# time.sleep(.5)
	fhand.close()
	print "********* FILE CLOSE {step} **************".format(step=job_package['step'])

	# return results
	return "File written"



