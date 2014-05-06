# code related to jobs

# dep
import redis
import pickle
# proj
import models

# redis handle
r_batch_handle = redis.StrictRedis(host='localhost', port=6379, db=2)

def jobStart():
	# increment and get job num
	job_num = r_batch_handle.incr("job_num")
	print "Beginning job #",job_num
	jobHand = models.jobBlob(job_num)
	return jobHand

def jobUpdate(jobHand):
	# push jobBlob to redis /2 / need to pickle first
	jobHand_pickled = pickle.dumps(jobHand)
	r_batch_handle.set("job_{job_num}".format(job_num=jobHand.job_num),jobHand_pickled)

def jobGet(job_num):
	# retrieving and unpickling from redis	
	jobHand_pickled = r_batch_handle.get("job_{job_num}".format(job_num=job_num))
	jobHand = pickle.loads(jobHand_pickled)	
	return jobHand