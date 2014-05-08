from wtforms import Form, BooleanField, StringField, validators

class pidSelection(Form):
    username = StringField('Username')
    PID = StringField('PID')
    