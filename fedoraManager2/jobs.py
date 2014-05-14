# code related to jobs

# dep
import redis
import pickle
# proj
import models
from redisHandles import *
from fedoraManager2 import db, db_con

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


# job objects
def jobUpdate(jobHand):
	jobHand_pickled = pickle.dumps(jobHand)
	r_job_handle.set("job_{job_num}".format(job_num=jobHand.job_num),jobHand_pickled)

def jobGet(job_num):	
	# IDEA: could query redis for r_job_handle.keys(job_num matching)!
	jobHand_pickled = r_job_handle.get("job_{job_num}".format(job_num=job_num))
	jobHand = pickle.loads(jobHand_pickled)	
	return jobHand

# task objects
def taskUpdate(taskHand):		
	taskHand_pickled = pickle.dumps(taskHand)				
	r_job_handle.set("taskStatus_{job_num}".format(job_num=taskHand.job_num),taskHand_pickled)	

def taskGet(job_num):
	taskHand_pickled = r_job_handle.get("taskStatus_{job_num}".format(job_num=job_num))
	taskHand = pickle.loads(taskHand_pickled)	
	completed_tasks = r_job_handle.keys("task*job_num{job_num}".format(job_num=job_num))
	taskHand.completed_tasks = 	completed_tasks	
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



# PID selection - SQL style
############################################################################################################
# def sendSelectedPIDs(username,PIDs):
# 	print "Storing selected PIDs for {username}".format(username=username)				
# 	for PID in PIDs:
# 		db.session.add(models.selectedPID(PID))	
# 	db.session.commit() # a failed commit while fail the whole lot
# 	print "PIDs stored"	

# def userPagGen(username):
# 	return ListPaginator(r_selectedPIDs_handle, "{username}_selectedPIDs".format(username=username), 10)
























