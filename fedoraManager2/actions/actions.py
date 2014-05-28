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

	# get and iterate through user selectedPIDs
	userPID_pag = models.user_pids.query.paginate(1,5)
	# userPID_pag = kwargs['userPID_pag']	
	
	step = 1	
	while userPID_pag.page < (userPID_pag.pages + 1):
		
		# iterate through PIDs in userPID_pag page
		for PID in userPID_pag.items:			
			print "Operating on PID:",PID.PID," / Step:",step		
			job_package['step'] = step			
			# fire off async task		
			result = kwargs['task_function'].delay(job_package)				
			# push result to jobHand
			job_package['jobHand'].assigned_tasks.append(result)
			# updates jobHand in redis so that polling process get up-to-date reflection of tasks added
			jobs.jobUpdate(job_package['jobHand'])
			step += 1

		# next page
		userPID_pag = userPID_pag.next()
		print "next page..."		



@celery.task()
def sampleTask(job_package):

	username = job_package['username']
	print "Starting sampleTask",job_package['step']
	
	# delay for testing	
	time.sleep(.25)	
	
	# update taskHand about task	
	redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "triggered")	

	# return results
	return 40 + 2


@celery.task()
def sampleFastTask(job_package):

	username = job_package['username']
	print "Starting sampleFastTask",job_package['step']
	
	# delay for testing	
	# time.sleep(.25)	
	
	# update taskHand about task	
	redisHandles.r_job_handle.set("task{step}_job_num{job_num}".format(step=job_package['step'],job_num=job_package['job_num']), "triggered")	

	# return results
	return 40 + 2






		

















