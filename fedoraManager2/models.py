from fedoraManager2 import db


class jobBlob:
	def __init__(self, job_num):
		self.job_num = job_num
		self.estimated_tasks = ''
		self.assigned_tasks = []
		self.pending_tasks = []
		self.completed_tasks = []
		self.error_tasks = []

class taskBlob:
	def __init__(self, job_num):
		self.job_num = job_num		
		self.estimated_tasks = ''
		self.last_completed_task_num = 'pending'
		self.completed_tasks = []



class user_pids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    PID = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255))

    def __init__(self, PID, username):
        self.PID = PID        
        self.username = username

    def __repr__(self):
        return '<PID %r>' % self.PID