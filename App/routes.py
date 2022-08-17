from crypt import methods
from datetime import datetime
from email.message import Message
from unicodedata import name
from flask import redirect, render_template, url_for, flash, request

# from turtle import rt, title

from flask_login import current_user, login_required, login_user, logout_user

from werkzeug.urls import url_parse

from App import app, db
from App.forms import Edit_User_Form, EmptyForm, LoginForm, RegisterForm, Add_FPSOForm, FpsoDetailForm, SearchForm, ResetPasswordRequestForm, ResetPasswordForm
from App.models import User, Fpso
from App.email import send_password_reset_email

import os

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        search_for=form.search_for.data
        return redirect(url_for('search', fpso = search_for))
    fpso = Fpso.query.order_by(Fpso.fpso_name).all()
    return render_template('index.html', title="Home", fpsos=fpso, form=form)

# SEARCH FOR FPSO
@app.route('/search/<fpso>', methods=['GET', 'POST'])
def search(fpso):
    form = SearchForm()
    search_FPSO = Fpso.query.filter(Fpso.fpso_name.like('%' + fpso + '%')).all()
    return render_template('search.html', fpso=search_FPSO, form=form, fp=fpso)


# ADD NEW FPSO
@app.route('/addfpso', methods=['GET', 'POST'])
@login_required
def addfpso():
    form = Add_FPSOForm()
    if form.validate_on_submit():
        fpso = Fpso.query.filter_by(fpso_name=form.name.data).first()
        if fpso == None:
            newfpso = Fpso(fpso_name=form.name.data, fpso_owner = current_user.username)
            db.session.add(newfpso)
            db.session.commit()
            form.name.data = ""
            flash(newfpso.fpso_name + ' Added. Please fill up remaining details and press Save button.')
            return redirect(url_for('general_details', fpso=newfpso.fpso_name))
        else:
            db.session.rollback()
            form.name.data = ""
            flash('FPSO with this name already exists. Find FPSO on the main page and press EDIT to update!')
    return render_template("add_fpso.html", title="Add New FPSO", form=form)


# ADD TO FAVORITE
@app.route('/add_to_favorite/<int:id>', methods=['GET', 'POST'])
@login_required
def add_to_favorite(id):
    form=EmptyForm()
    if form.validate_on_submit():
        fpso_to_add = Fpso.query.filter_by(id=id).first()
        if fpso_to_add is None:
            flash('FPSO {} not found'.format(fpso_to_add.fpso_name))
            return redirect(url_for('index'))
        current_user.add_to_favorite(fpso_to_add)
        db.session.commit()
        flash('You are following {}'.format(fpso_to_add.fpso_name))
        return redirect(url_for('index'))

# REMOVE FORM FAVORITE
@app.route('/remove_from_favorite/<int:id>', methods=['GET', 'POST'])
@login_required
def remove_from_favorite(id):
    form=EmptyForm()
    if form.validate_on_submit():
        fpso_to_remove = Fpso.query.filter_by(id=id).first()
        if fpso_to_remove is None:
            flash('FPSO {} not found'.format(fpso_to_remove.fpso_name))
            return redirect(url_for('index'))
        current_user.remove_from_favorite(fpso_to_remove)
        db.session.commit()
        flash('You are no longer following {}'.format(fpso_to_remove.fpso_name))
        return redirect(url_for('dashboard', username=current_user.username))

# DASHBOARD
@app.route('/user_dashboard/<username>')
@login_required
def dashboard(username):
    admin = os.environ.get("ADMIN")
    user = User.query.filter_by(username = username).first_or_404()
    followed_fpso = user.favorite_fpso()
    return render_template('dashboard.html', title='User Dashboard', user=user, fpsos=followed_fpso, admin=admin)

# ALL USERS
@app.route('/all_users', methods=['GET', 'POST'])
def all_users():
    users = User.query.order_by(User.user_since).all()
    return render_template('all_users.html', title = 'All Users', users=users)

# DELETE WARNING PAGE
@app.route('/delete_warning<int:id>')
@login_required
def delete_warning(id):
     fpso_to_delete = Fpso.query.get_or_404(id)
     return render_template('delete_fpso.html', title='Delete_FPSO', fpso=fpso_to_delete)
    

# DELETE FPSO
@app.route('/delete_fpso/<int:id>')
@login_required
def delete_fpso(id):
    fpso_to_delete = Fpso.query.get_or_404(id)
    try:
        flash(fpso_to_delete.fpso_name + ' Deleted!')
        db.session.delete(fpso_to_delete)
        db.session.commit()
        # qury all FPSOs
        return redirect(url_for('index'))
    except:
        flash('Somthing want wrong when deleting the FPSO')
        # query FPSO
        return redirect('index')


# DELETE USER WARNING PAGE
@app.route('/delete_user_warning<int:id>')
@login_required
def delete_User_warning(id):
     user_to_delete = User.query.get_or_404(id)
     return render_template('delete_user.html', title='Delete_User', user=user_to_delete)

# DELETE USER
@app.route('/delete_user/<int:id>')
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    try:
        flash('{} deleted!!!'.format(user_to_delete.username))
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('login'))
    except:
        flash('{} not found!!!'.format(user_to_delete.username))
        db.session.rollback()
        return redirect(url_for('index'))


# EDIT FPSO
@app.route('/edit_fpso/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_fpso(id):

    form = FpsoDetailForm(email_1 = 'fpso@example.com', email_2='fpso@example.com', email_3='fpso@example.com', email_4='fpso@example.com', email_5='fpso@example.com')
    fpso_to_edit = Fpso.query.get_or_404(id)
    admin = os.environ.get("ADMIN")

    if fpso_to_edit == None:
        flash('There no FPSO with such a name!!!')
        return redirect('index')

    if form.validate_on_submit():
        fpso_to_edit.fpso_owner = current_user.username
        fpso_to_edit.fpso_img_name = form.img_name.data
        fpso_to_edit.fpso_name = form.name.data
        fpso_to_edit.fpso_remarks = form.fpso_details.data
        fpso_to_edit.timestamp = datetime.utcnow()
        fpso_to_edit.fpso_basin = form.basin.data
        fpso_to_edit.fpso_psn_lat_deg = form.psn_lat_deg.data
        fpso_to_edit.fpso_psn_lat_min = form.psn_lat_min.data
        fpso_to_edit.fpso_psn_lat_sec = form.psn_lat_sec.data
        fpso_to_edit.fpso_psn_lat_NS = form.psn_lat_NS.data
        fpso_to_edit.fpso_psn_long_deg = form.psn_long_deg.data
        fpso_to_edit.fpso_psn_long_min = form.psn_long_min.data
        fpso_to_edit.fpso_psn_long_sec = form.psn_long_sec.data
        fpso_to_edit.fpso_psn_long_WE = form.psn_long_WE.data
        fpso_to_edit.fpso_hdg = form.hdg.data
        fpso_to_edit.fpso_disch_rate = form.disch_rate.data
        fpso_to_edit.fpso_vhf = form.vhf.data
        fpso_to_edit.fpso_email_1 = form.email_1.data
        fpso_to_edit.fpso_email_2 = form.email_2.data
        fpso_to_edit.fpso_email_3 = form.email_3.data
        fpso_to_edit.fpso_email_4 = form.email_4.data
        fpso_to_edit.fpso_email_5 = form.email_5.data
        fpso_to_edit.cargo_name = form.cargo_name.data 
        fpso_to_edit.cargo_API = form.cargo_api.data
        fpso_to_edit.cargo_dens = form.cargo_dens.data
        fpso_to_edit.cargo_temp = form.cargo_temp.data
        fpso_to_edit.cargo_bsw = form.cargo_bsw.data
        fpso_to_edit.cargo_line_displ_fwd = form.cargo_line_displ_fwd.data
        fpso_to_edit.cargo_Hose_Flush_fwd = form.cargo_Hose_Flush_fwd.data
        fpso_to_edit.cargo_line_displ_aft = form.cargo_line_displ_aft.data
        fpso_to_edit.cargo_Hose_Flush_aft = form.cargo_Hose_Flush_aft.data
        fpso_to_edit.cargo_info = form.cargo_info.data
        fpso_to_edit.darps_ID_fwd = form.darps_ID_fwd.data
        fpso_to_edit.darps_1_tdma_fwd = form.darps_1_tdma_fwd.data
        fpso_to_edit.darps_2_tdma_fwd = form.darps_2_tdma_fwd.data
        fpso_to_edit.darps_info_fwd = form.darps_info_fwd.data
        fpso_to_edit.darps_1_ts_fwd = form.darps_1_ts_fwd.data
        fpso_to_edit.darps_2_ts_fwd = form.darps_2_ts_fwd.data
        fpso_to_edit.artemis_address_code_fwd = form.artemis_address_code_fwd.data
        fpso_to_edit.artemis_freq_pair_fwd = form.artemis_freq_pair_fwd.data
        fpso_to_edit.artemis_info_fwd = form.artemis_info_fwd.data
        fpso_to_edit.fanbeam_info_fwd = form.fanbeam_info_fwd.data
        fpso_to_edit.radius_info_fwd = form.radius_info_fwd.data
        fpso_to_edit.darps_ID_aft = form.darps_ID_aft.data
        fpso_to_edit.darps_1_tdma_aft = form.darps_1_tdma_aft.data
        fpso_to_edit.darps_2_tdma_aft = form.darps_2_tdma_aft.data
        fpso_to_edit.darps_info_aft = form.darps_info_aft.data
        fpso_to_edit.darps_1_ts_aft = form.darps_1_ts_aft.data
        fpso_to_edit.darps_2_ts_aft = form.darps_2_ts_aft.data
        fpso_to_edit.artemis_address_code_aft = form.artemis_address_code_aft.data
        fpso_to_edit.artemis_freq_pair_aft = form.artemis_freq_pair_aft.data
        fpso_to_edit.artemis_info_aft = form.artemis_info_aft.data
        fpso_to_edit.fanbeam_info_aft = form.fanbeam_info_aft.data
        fpso_to_edit.radius_info_aft = form.radius_info_aft.data
        db.session.commit()
        flash(fpso_to_edit.fpso_name + ' Updated')
        return redirect(url_for('index'))
    elif request.method =="GET": 
        form.name.data = fpso_to_edit.fpso_name
        form.img_name.data = fpso_to_edit.fpso_img_name
        form.fpso_details.data = fpso_to_edit.fpso_remarks
        form.basin.data = fpso_to_edit.fpso_basin
        form.psn_lat_deg.data = fpso_to_edit.fpso_psn_lat_deg
        form.psn_lat_min.data = fpso_to_edit.fpso_psn_lat_min
        form.psn_lat_sec.data = fpso_to_edit.fpso_psn_lat_sec
        form.psn_lat_NS.data = fpso_to_edit.fpso_psn_lat_NS
        form.psn_long_deg.data = fpso_to_edit.fpso_psn_long_deg 
        form.psn_long_min.data = fpso_to_edit.fpso_psn_long_min
        form.psn_long_sec.data = fpso_to_edit.fpso_psn_long_sec 
        form.psn_long_WE.data = fpso_to_edit.fpso_psn_long_WE
        form.hdg.data = fpso_to_edit.fpso_hdg
        form.disch_rate.data = fpso_to_edit.fpso_disch_rate
        form.vhf.data = fpso_to_edit.fpso_vhf 
        form.email_1.data = fpso_to_edit.fpso_email_1
        form.email_2.data = fpso_to_edit.fpso_email_2
        form.email_3.data = fpso_to_edit.fpso_email_3
        form.email_4.data = fpso_to_edit.fpso_email_4
        form.email_5.data = fpso_to_edit.fpso_email_5
        form.cargo_name.data = fpso_to_edit.cargo_name
        form.cargo_api.data = fpso_to_edit.cargo_API
        form.cargo_dens.data = fpso_to_edit.cargo_dens
        form.cargo_temp.data = fpso_to_edit.cargo_temp
        form.cargo_bsw.data = fpso_to_edit.cargo_bsw
        form.cargo_line_displ_fwd.data = fpso_to_edit.cargo_line_displ_fwd
        form.cargo_Hose_Flush_fwd.data = fpso_to_edit.cargo_Hose_Flush_fwd
        form.cargo_line_displ_aft.data = fpso_to_edit.cargo_line_displ_aft
        form.cargo_Hose_Flush_aft.data = fpso_to_edit.cargo_Hose_Flush_aft
        form.cargo_info.data = fpso_to_edit.cargo_info
        form.darps_ID_fwd.data = fpso_to_edit.darps_ID_fwd
        form.darps_1_tdma_fwd.data = fpso_to_edit.darps_1_tdma_fwd
        form.darps_2_tdma_fwd.data = fpso_to_edit.darps_2_tdma_fwd
        form.darps_info_fwd.data = fpso_to_edit.darps_info_fwd
        form.darps_1_ts_fwd.data = fpso_to_edit.darps_1_ts_fwd
        form.darps_2_ts_fwd.data = fpso_to_edit.darps_2_ts_fwd
        form.artemis_address_code_fwd.data = fpso_to_edit.artemis_address_code_fwd
        form.artemis_freq_pair_fwd.data = fpso_to_edit.artemis_freq_pair_fwd
        form.artemis_info_fwd.data = fpso_to_edit.artemis_info_fwd
        form.fanbeam_info_fwd.data = fpso_to_edit.fanbeam_info_fwd
        form.radius_info_fwd.data = fpso_to_edit.radius_info_fwd
        form.darps_ID_aft.data = fpso_to_edit.darps_ID_aft
        form.darps_1_tdma_aft.data = fpso_to_edit.darps_1_tdma_aft
        form.darps_2_tdma_aft.data = fpso_to_edit.darps_2_tdma_aft
        form.darps_info_aft.data = fpso_to_edit.darps_info_aft
        form.darps_1_ts_aft.data = fpso_to_edit.darps_1_ts_aft
        form.darps_2_ts_aft.data =  fpso_to_edit.darps_2_ts_aft
        form.artemis_address_code_aft.data = fpso_to_edit.artemis_address_code_aft
        form.artemis_freq_pair_aft.data = fpso_to_edit.artemis_freq_pair_aft
        form.artemis_info_aft.data = fpso_to_edit.artemis_info_aft
        form.fanbeam_info_aft.data = fpso_to_edit.fanbeam_info_aft
        form.radius_info_aft.data = fpso_to_edit.radius_info_aft

    return render_template('edit_fpso.html', title='Edit FPSO', fpso = fpso_to_edit, form = form, admin=admin)

# EDIT USER
@app.route('/edit_user/<username>', methods=['GET', 'POST'])
def edit_user(username):
    form=Edit_User_Form()
    user_to_edit = User.query.filter_by(username=username).first()
    if user_to_edit is None:
        flash('{} not found!!!'.format(user_to_edit.username))
        return('index')
    if form.validate_on_submit():
        user_to_edit.user_name = form.name.data
        user_to_edit.user_surname = form.surname.data
        user_to_edit.username = form.username.data
        user_to_edit.user_email = form.email.data
        db.session.commit()
        flash('user {} updated'.format(user_to_edit.username))
        return redirect(url_for('dashboard', username=current_user.username))
    form.name.data = user_to_edit.user_name
    form.surname.data = user_to_edit.user_surname
    form.username.data = user_to_edit.username
    form.email.data = user_to_edit.user_email

    return render_template('edit_user.html', title='Edit User', form=form, user=user_to_edit)
    

# FPSO PAGE
@app.route('/fpso/<id>')
def fpso_page(id):
    form = EmptyForm()
    fpso = Fpso.query.get_or_404(id)
    return render_template('fpso_page.html', fpso=fpso, title='FPSO_Page', form=form)


# FPSO DETAILS PAGE
@app.route('/fpso_details<fpso>', methods=['GET', 'POST'])
def general_details(fpso):
    form = FpsoDetailForm(email_1 = 'fpso@example.com', email_2='fpso@example.com', email_3='fpso@example.com', email_4='fpso@example.com', email_5='fpso@example.com')
    fpso_to_update = Fpso.query.filter_by(fpso_name=fpso).first()
    if fpso_to_update == None:
        return redirect(url_for('addfpso'))
    form.name.data = fpso_to_update.fpso_name
    if form.validate_on_submit():
        fpso_to_update.fpso_name = form.name.data
        fpso_to_update.fpso_img_name = 'default_fpso_card'
        fpso_to_update.fpso_remarks = form.fpso_details.data
        fpso_to_update.timestamp = datetime.utcnow()
        fpso_to_update.fpso_basin = form.basin.data
        fpso_to_update.fpso_psn_lat_deg = form.psn_lat_deg.data
        fpso_to_update.fpso_psn_lat_min = form.psn_lat_min.data
        fpso_to_update.fpso_psn_lat_sec = form.psn_lat_sec.data
        fpso_to_update.fpso_psn_lat_NS = form.psn_lat_NS.data
        fpso_to_update.fpso_psn_long_deg = form.psn_long_deg.data
        fpso_to_update.fpso_psn_long_min = form.psn_long_min.data
        fpso_to_update.fpso_psn_long_sec = form.psn_long_sec.data
        fpso_to_update.fpso_psn_long_WE = form.psn_long_WE.data
        fpso_to_update.fpso_hdg = form.hdg.data
        fpso_to_update.fpso_disch_rate = form.disch_rate.data
        fpso_to_update.fpso_vhf = form.vhf.data
        fpso_to_update.fpso_email_1 = form.email_1.data
        fpso_to_update.fpso_email_2 = form.email_2.data
        fpso_to_update.fpso_email_3 = form.email_3.data
        fpso_to_update.fpso_email_4 = form.email_4.data
        fpso_to_update.fpso_email_5 = form.email_5.data
        fpso_to_update.cargo_name = form.cargo_name.data 
        fpso_to_update.cargo_API = form.cargo_api.data
        fpso_to_update.cargo_dens = form.cargo_dens.data
        fpso_to_update.cargo_temp = form.cargo_temp.data
        fpso_to_update.cargo_bsw = form.cargo_bsw.data
        fpso_to_update.cargo_line_displ_fwd = form.cargo_line_displ_fwd.data
        fpso_to_update.cargo_Hose_Flush_fwd = form.cargo_Hose_Flush_fwd.data
        fpso_to_update.cargo_line_displ_aft = form.cargo_line_displ_aft.data
        fpso_to_update.cargo_Hose_Flush_aft = form.cargo_Hose_Flush_aft.data
        fpso_to_update.cargo_info = form.cargo_info.data
        fpso_to_update.darps_ID_fwd = form.darps_ID_fwd.data
        fpso_to_update.darps_1_tdma_fwd = form.darps_1_tdma_fwd.data
        fpso_to_update.darps_2_tdma_fwd = form.darps_2_tdma_fwd.data
        fpso_to_update.darps_info_fwd = form.darps_info_fwd.data
        fpso_to_update.darps_1_ts_fwd = form.darps_1_ts_fwd.data
        fpso_to_update.darps_2_ts_fwd = form.darps_2_ts_fwd.data
        fpso_to_update.artemis_address_code_fwd = form.artemis_address_code_fwd.data
        fpso_to_update.artemis_freq_pair_fwd = form.artemis_freq_pair_fwd.data
        fpso_to_update.artemis_info_fwd = form.artemis_info_fwd.data
        fpso_to_update.fanbeam_info_fwd = form.fanbeam_info_fwd.data
        fpso_to_update.radius_info_fwd = form.radius_info_fwd.data
        fpso_to_update.darps_ID_aft = form.darps_ID_aft.data
        fpso_to_update.darps_1_tdma_aft = form.darps_1_tdma_aft.data
        fpso_to_update.darps_2_tdma_aft = form.darps_2_tdma_aft.data
        fpso_to_update.darps_info_aft = form.darps_info_aft.data
        fpso_to_update.darps_1_ts_aft = form.darps_1_ts_aft.data
        fpso_to_update.darps_2_ts_aft = form.darps_2_ts_aft.data
        fpso_to_update.artemis_address_code_aft = form.artemis_address_code_aft.data
        fpso_to_update.artemis_freq_pair_aft = form.artemis_freq_pair_aft.data
        fpso_to_update.artemis_info_aft = form.artemis_info_aft.data
        fpso_to_update.fanbeam_info_aft = form.fanbeam_info_aft.data
        fpso_to_update.radius_info_aft = form.radius_info_aft.data
        db.session.commit()
        flash(fpso_to_update.fpso_name + ' Added')
        return redirect(url_for('index'))
    return render_template('fpso_details.html', form=form, fpso = fpso_to_update)

# LOGIN VIEW FUNCTION
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # checks if user exists and if password matches
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('login'))
        login_user(user)
        # use next arg to return ulogged user to the requested page after succesfull loggin
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('dashboard', username=user.username))
    return render_template('login.html', form=form, title='Login')

# LOGOUT
@app.route('/logout')
def logout():
    logout_user()
    return redirect('index')

# RESET PASSWORD REQUEST
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email = form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instruction to reset your password")
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form, title="Reset Password")

# PASSWORD REQUEST LINK
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your Password has been reset.")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

# REGISTER VIEW FUNCTION
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect('index')
    if form.validate_on_submit():
        new_user = User(
                user_name = form.name.data,
                user_surname = form.surname.data,
                username = form.username.data,
                user_email = form.email.data,
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Congratulation, You are now  the registered User. Please Login!!!")
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')