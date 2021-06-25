from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.fields.html5 import DateField
from wtforms_components import DateRange
from datetime import datetime, date

class SimpleForm(FlaskForm):
    textfield = StringField('Enter Your Name', default="")
    selectfield = SelectField("Select Operating System",
                              choices=[('Windows 10', 'Windows 10'), ('Ubuntu 2004', 'Ubuntu2004')])
    submit = SubmitField('Click Next')


class AnotherForm(FlaskForm):
    submit = SubmitField('Generate JSON & Trigger WR')

class ExampleForm(FlaskForm):
    submit = SubmitField('Click Here for WorkFlow')