from flask_wtf import FlaskForm
from pyparsing import Regex
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length, Regexp

from App.models import User


# EMPTY_FORM
# An empty for used to follow and unfollow thhe post
class EmptyForm(FlaskForm):
    submit=SubmitField('submit')

# LOGIN
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

# REGISTER
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Regexp('^[A-Za-a][A-Za-z0-9_.]*$', 0, 'Username must have only letters, numbers, dots or undersores)')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_user(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError("Username alredy exists. Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(user_email = email.data).first()
        if user is not None:
            raise ValidationError("Email alredy exists. Please use a different email address.")

# DASHBOARD
class Dashboard(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    user_blog = TextAreaField('About Me', validators = [Length(min=0, max=140)])

# EDIT USER PROFILE
class Edit_User_Form(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

# FPSO
class Add_FPSOForm(FlaskForm):
    name = StringField("FPSO name", validators=[DataRequired()])
    submit = SubmitField('Add New FPSO')

# FPSO DETAILS FORM
class FpsoDetailForm(FlaskForm):
    name = StringField("FPSO name", validators=[DataRequired()])
    img_name = StringField("Img Name")
    fpso_details = TextAreaField("General Info")
    basin = StringField("Basin")
    psn_lat_deg = StringField(" Deg ")
    psn_lat_min = StringField("Min")
    psn_lat_sec = StringField("Sec")
    psn_lat_NS = SelectField("N/S", choices=[('N', 'N'), ('S', 'S')])
    psn_long_deg = StringField("Deg")
    psn_long_min = StringField("Min")
    psn_long_sec = StringField("Sec")
    psn_long_WE = SelectField("W/S", choices=[('W', 'W'), ('E', 'E')])
    hdg = StringField('Heading')
    disch_rate = StringField('Discharging Rate')
    vhf = StringField('Operational Channel')
    email_1 = StringField('Emeil 1', validators=[Email()])
    email_2 = StringField('Emeil 2', validators=[Email()])
    email_3 = StringField('Emeil 3', validators=[Email()])
    email_4 = StringField('Emeil 4', validators=[Email()])
    email_5 = StringField('Emeil 5', validators=[Email()])
    # CARGO
    cargo_name = StringField("Cargo name", validators=[DataRequired()])
    cargo_api = StringField("API")
    cargo_dens = StringField("Dens @ 20deg")
    cargo_temp = StringField("Temp")
    cargo_bsw = StringField("BSW")
    cargo_line_displ_fwd = StringField('Quantity of Line Displacement')
    cargo_Hose_Flush_fwd = StringField('Quantity of Hose Flushing')
    cargo_line_displ_aft = StringField('Quantity of Line Displacement')
    cargo_Hose_Flush_aft = StringField('Quantity of Hose Flushing')
    cargo_info = TextAreaField("Info about Line displacement and Hose Flushing", validators=[Length(min=0, max=140)])
    # PRS
    darps_ID_fwd = StringField("ID")
    darps_1_tdma_fwd = StringField("TDMA 1")
    darps_2_tdma_fwd = StringField("TDMA 2")
    darps_info_fwd = TextAreaField("Usefull Information", validators=[Length(min=0, max=140)])
    darps_1_ts_fwd = StringField("Time Slot 1")
    darps_2_ts_fwd = StringField("Time Slot 2")
    artemis_address_code_fwd = StringField("Add Code")
    artemis_freq_pair_fwd = StringField("Freq Pair")
    artemis_info_fwd = TextAreaField("Info", validators=[Length(min=0, max=140)])
    fanbeam_info_fwd = TextAreaField("Info", validators=[Length(min=0, max=140)])
    radius_info_fwd = TextAreaField("Info", validators=[Length(min=0, max=140)])

    darps_ID_aft = StringField("ID")
    darps_1_tdma_aft = StringField("TDMA 1")
    darps_2_tdma_aft = StringField("TDMA 2")
    darps_info_aft = TextAreaField("Usefull Information", validators=[Length(min=0, max=140)])
    darps_1_ts_aft = StringField("Time Slot 1")
    darps_2_ts_aft = StringField("Time Slot 2")
    artemis_address_code_aft = StringField("Add Code")
    artemis_freq_pair_aft = StringField("Freq Pair")
    artemis_info_aft = TextAreaField("Info", validators=[Length(min=0, max=140)])
    fanbeam_info_aft = TextAreaField("Info", validators=[Length(min=0, max=140)])
    radius_info_aft = TextAreaField("Info", validators=[Length(min=0, max=140)])

    submit = SubmitField('Save')

# SEARCH FORM
class SearchForm(FlaskForm):
    search_for = StringField('search for', validators=[DataRequired()])
    submit = SubmitField('Search')
