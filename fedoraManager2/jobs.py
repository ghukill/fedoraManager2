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

	# instatiate handles for job and status of tasks
	jobHand = models.jobBlob(job_num)
	taskHand = models.taskBlob(job_num)
	return {"jobHand":jobHand,"taskHand":taskHand}


def jobUpdate(jobHand):
	jobHand_pickled = pickle.dumps(jobHand)
	r_job_handle.set("job_{job_num}".format(job_num=jobHand.job_num),jobHand_pickled)

def taskUpdate(taskHand):		
	taskHand_pickled = pickle.dumps(taskHand)				
	r_job_handle.set("taskStatus_{job_num}".format(job_num=taskHand.job_num),taskHand_pickled)	

def jobGet(job_num):	
	jobHand_pickled = r_job_handle.get("job_{job_num}".format(job_num=job_num))
	jobHand = pickle.loads(jobHand_pickled)	
	return jobHand

def taskGet(job_num):
	taskHand_pickled = r_job_handle.get("taskStatus_{job_num}".format(job_num=job_num))
	taskHand = pickle.loads(taskHand_pickled)		
	return taskHand


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


























