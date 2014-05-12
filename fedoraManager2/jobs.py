# code related to jobs

# dep
import redis
import pickle
# proj
import models
from redisHandles import *

# zato paginator
from zato.redis_paginator import ListPaginator, ZSetPaginator


# Job Management
############################################################################################################
def jobStart():
	# increment and get job num
	job_num = r_job_handle.incr("job_num")
	print "Beginning job #",job_num
	jobHand = models.jobBlob(job_num)
	jobStatusHand = models.jobBlob(job_num)
	return {"jobHand":jobHand,"jobStatusHand":jobStatusHand}

def jobUpdate(jobHand):	

	'''
	Add username instead of 'job'?
	Yes, this would be a good backup to the SQL table that will be holding the jobs as well.
	'''

	jobHand_pickled = pickle.dumps(jobHand)
	r_job_handle.set("job_{job_num}".format(job_num=jobHand.job_num),jobHand_pickled)

def jobStatusUpdate(jobStatusHand):	
	
	try:		
		print "This is the jobStatusHand",jobStatusHand.completed_tasks
		jobStatusHand_pickled = pickle.dumps(jobStatusHand)				
		r_job_handle.set("jobStatus_{job_num}".format(job_num=jobStatusHand.job_num),jobStatusHand_pickled)		
	except:
		print "there was an error here."

def jobGet(job_num):
	# retrieving and unpickling from redis	
	jobHand_pickled = r_job_handle.get("job_{job_num}".format(job_num=job_num))
	jobHand = pickle.loads(jobHand_pickled)	

	jobStatusHand_pickled = r_job_handle.get("jobStatus_{job_num}".format(job_num=job_num))
	jobStatusHand = pickle.loads(jobStatusHand_pickled)		
	return {'jobHand':jobHand,'jobStatusHand':jobStatusHand}



# PID selection
############################################################################################################
def sendSelectedPIDs(username,PIDs):
	print "Storing selected PIDs for {username}".format(username=username)	
	pipe = r_selectedPIDs_handle.pipeline()
	for PID in PIDs:
		# CONSIDER USING SETS HERE "SAAD"		
		pipe.lpush("{username}_selectedPIDs".format(username=username),PID)
	pipe.execute()
	print "PIDs stored."

def userPagGen(username):
	return ListPaginator(r_selectedPIDs_handle, "{username}_selectedPIDs".format(username=username), 10)


























