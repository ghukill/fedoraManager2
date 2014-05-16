from cl.cl import celery
import redis

import fedoraManager2.jobs as jobs
import fedoraManager2.redisHandles as redisHandles

# local dependecies
import time
import sys




@celery.task()
def celeryTaskFactory(**kwargs):
	
	# create job_package
	job_package = kwargs['job_package']

	# get user selectedPIDs	
	
		

	# run task by iterating through userPag (Paginator object)
	step = 1	
	while step < (userPag.count + 1):			

		job_package['step'] = step
		print "Firing off task:",step		
		# fire off async task		
		result = kwargs['task_function'].delay(job_package)				

		# push result to jobHand
		job_package['jobHand'].assigned_tasks.append(result)
		jobs.jobUpdate(job_package['jobHand'])

		step += 1


# MOVING INTO SQL 
##################################################################################################################################
# @celery.task()
# def celeryTaskFactory(**kwargs):
	
# 	# create job_package
# 	job_package = kwargs['job_package']

# 	# get selectedPIDs	
# 	userPag = jobs.userPagGen(job_package['username'])	
# 	print "Found {count} PIDs for {username}".format(count=userPag.count,username=job_package['username'])	

# 	# run task by iterating through userPag (Paginator object)
# 	step = 1	
# 	while step < (userPag.count + 1):			

# 		job_package['step'] = step
# 		print "Firing off task:",step		
# 		# fire off async task		
# 		result = kwargs['task_function'].delay(job_package)				

# 		# push result to jobHand
# 		job_package['jobHand'].assigned_tasks.append(result)
# 		jobs.jobUpdate(job_package['jobHand'])

# 		step += 1
##################################################################################################################################


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




		

















