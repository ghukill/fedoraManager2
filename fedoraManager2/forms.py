from wtforms import Form, BooleanField, StringField, validators, fields

class PIDselection(Form):
    # username = StringField('Username')
    PID = fields.FieldList(fields.TextField(('PID')), min_entries=3)
    