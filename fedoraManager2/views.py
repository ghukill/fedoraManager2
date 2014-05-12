from fedoraManager2 import app
from fedoraManager2 import models
from fedoraManager2.actions import actions

# flask proper
from flask import render_template, request, session, redirect

# forms
from flask_wtf import Form
from wtforms import TextField

# zato paginator
from zato.redis_paginator import ListPaginator, ZSetPaginator

import time
import json
import pickle
import sys

# get celery instance / handle
from cl.cl import celery
import jobs
import forms
from redisHandles import *

from uuid import uuid4

# fake session data
####################################
# set the secret key
app.secret_key = 'ShoppingHorse'
####################################

@app.route("/")
def index():
	return render_template("index.html")
	


@app.route("/task_status/<task_id>")
def task_status(task_id):
	
	# global way to surgically pick task out of celery memory		
	result = actions.celery.AsyncResult(task_id)	
	state, retval = result.state, result.result
	response_data = dict(id=task_id, status=state, result=retval)
	
	return json.dumps(response_data)


	return "You are looking for {task_id}".format(task_id=task_id)	



@app.route("/job_status/<job_num>")
def job_status(job_num):			
	
	# start timer
	stime = time.time()

	# get job
	jobHand = jobs.jobGet(job_num)['jobHand']
	jobHandStatus = jobs.jobGet(job_num)['jobStatusHand']

	# check if pending jobs done
	if len(jobHand.pending_tasks) == 0:
		return "Job Complete!"
	
	# check if job has started at all!
	job_start_result = celery.AsyncResult(jobHand.assigned_tasks[0])				
	state = job_start_result.state
	print "Checking if job started..."
	if state == "PENDING":
		print "Job Pending."
		return "Job Pending, waiting for others to complete.  Isn't that polite?"

	# else, check all pending jobs
	print "Pre routing length of pending list",len(jobHand.pending_tasks)	
	pending_worker = jobHand.pending_tasks[:] 
	for task in pending_worker:		
		result = celery.AsyncResult(task)				
		state = result.state
		print "Checking task:",task,"/ State:",state
		
		# route based on state
		if state == "SUCCESS":
			jobHand.pending_tasks.remove(task)
			jobHand.completed_tasks.append(task)		

	print "POST routing length of pending list",len(jobHand.pending_tasks)

	etime = time.time()
	ttime = (etime - stime) * 1000
	print "Pending / Completion check took",ttime,"ms"	

	# update job
	jobs.jobUpdate(jobHand)	

	# check status	
	return "{completed} / {total} Completed.".format(completed=len(jobHand.completed_tasks),total=len(jobHand.assigned_tasks))

@app.route("/job_statusv2/<job_num>")
def job_statusv2(job_num):		
	
	# start timer
	stime = time.time()

	# get job
	jobHand = jobs.jobGet(job_num)['jobHand']
	jobStatusHand = jobs.jobGet(job_num)['jobStatusHand']

	# check if pending jobs done
	if  jobStatusHand.completed_tasks[0] == jobStatusHand.estimated_tasks:
		return "Job Complete!"
	
	if len(jobStatusHand.completed_tasks) < 1:
		print "Job Pending, waiting for others to complete.  Isn't that polite?"
		return "Job Pending, waiting for others to complete.  Isn't that polite?"

	etime = time.time()
	ttime = (etime - stime) * 1000
	print "Pending / Completion check took",ttime,"ms"

	# check status	
	return "{completed} / {total} Completed.".format(completed=jobStatusHand.completed_tasks[0],total=jobStatusHand.estimated_tasks)


# Session Testing
@app.route("/sessionSet/<username>")
def sessionSet(name):	
	session['username'] = username
	return "You have changed the session username to {username}.".format(username=username)

@app.route("/sessionCheck")
def sessionCheck():		
	username = session['username']
	return "You have retrieved the session username {username}.".format(username=username)

@app.route('/userPage/<username>')
def userPage(username):
	# set username in session
	session['username'] = username	

	# info to render page
	userData = {}
	userData['username'] = username
	return render_template("userPage.html",userData=userData)

# Make the following: quickAddUser, longAddUser, PIDselectionUser
@app.route("/quickAddUser")
def quickAddUser():
	print "Starting request..."
	
	username = session['username']	
	userPag = jobs.userPagGen(username)	

	# instatiate jobHand object
	jobPlatter = jobs.jobStart()
	jobHand = jobPlatter['jobHand']
	jobStatusHand = jobPlatter['jobStatusHand']

	# begin job
	count = 1
	print "Antipcating",userPag.count,"tasks...."
	jobHand.estimated_tasks = userPag.count	
	jobStatusHand.estimated_tasks = (userPag.count - 1) #count is human readable, NOT length of list
	while count < userPag.count:				
		result = actions.quickAdd.delay(jobStatusHand, 41, 1, count)		
		jobHand.assigned_tasks.append(str(result)) 
		print count, result				
		count += 1				

	# copy all tasks to pending
	jobHand.pending_tasks = jobHand.assigned_tasks[:] 

	print "Finished job #",jobHand.job_num		

	# update job
	jobs.jobUpdate(jobHand) 

	return "You have initiated job {job_num}.  Click <a href='/job_statusv2/{job_num}'>here</a> to check it foo.".format(job_num=jobHand.job_num)


# Make the following: quickAddUser, longAddUser, PIDselectionUser
@app.route("/quickAddUserFactory")
def quickAddUserFactory():
	print "Starting request..."
	
	username = session['username']	
	userPag = jobs.userPagGen(username)	

	# instatiate jobHand object
	jobPlatter = jobs.jobStart()
	jobHand = jobPlatter['jobHand']
	jobStatusHand = jobPlatter['jobStatusHand']

	# begin job
	jobHand.estimated_tasks = userPag.count	
	task_package = {		
		"jobStatusHand":jobStatusHand,		
		"a":41,
		"b":1
	}
	result = actions.celeryTaskFactory.delay(username=username,task_name="quickAddFactory",task_function=actions.quickAddFactory,task_package=task_package)	

	print "Finished job #",jobHand.job_num			

	return "You have initiated job {job_num} via the Factory.  Click <a href='/job_statusv2/{job_num}'>here</a> to check it foo.".format(job_num=jobHand.job_num)



# PID selection sandboxing
@app.route("/PIDselectionUser", methods=['POST', 'GET'])
def PIDselectionUser():
	# get username from session
	username = session['username']
	form = forms.PIDselection(request.form)
	if request.method == 'POST':		
		PID = form.PID.data		
		# send PIDs to Redis
		jobs.sendSelectedPIDs(username,PID)
		return redirect("/PIDcheckUser/1".format(username=username))
		return "We've got form data, your username is {username}, and your PIDs are {PID}.".format(username=username,PID=PID)                
	return render_template('PIDformUser.html', username=username, form=form)

# PID check for user
@app.route("/PIDcheckUser/<pagenum>")
def PIDcheckUser(pagenum):
	# start timer
	stime = time.time()

	# get username from session
	username = session['username']	

	# entirety of pagination code - lightning fast, can break this out somewhere else	
	userPag = jobs.userPagGen(username)	
	print "Found {count} PIDs for {username}".format(count=userPag.count,username=username)
	print "Paginator is",sys.getsizeof(userPag),"bytes"
	print "You have {PID_count} PIDs, will need {page_count} pages.".format(PID_count=userPag.count,page_count=userPag.num_pages)				
	cpage = userPag.page(pagenum)	

	# report time passed	
	etime = time.time()
	ttime = (etime - stime) * 1000
	print "PID retrieval took",ttime,"ms"	

	# pass the current PIDs to page as list	
	return render_template("PIDcheckUser.html",cpage_PIDs=cpage.object_list,username=username,userPag=userPag,cpage=cpage,pagenum=int(pagenum))

# Catch all - DON'T REMOVE
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return render_template("404.html")













