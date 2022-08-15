from email.policy import default
from enum import unique
from App import db, login, app
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt


# Setting the logged user for Flask Login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Setting up the followers assosiated table for many to many DB model
favorite = db.Table('favorite',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('fpso_id', db.Integer, db.ForeignKey('fpso.id'))
    )

# SETTTING UP THE USER MODEL
class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, index=True)
    user_surname = db.Column(db.String, index=True)
    username = db.Column(db.String, index=True, unique=True)
    user_email = db.Column(db.String, index=True, unique=True)
    user_blog = db.Column(db.String, index=True)
    user_password_hash = db.Column(db.String(128))
    user_since = db.Column(db.DateTime, default=datetime.utcnow)
    user_last_seen= db.Column(db.DateTime, default=datetime.utcnow)
    favorite = db.relationship('Fpso', secondary=favorite, backref='followers', lazy='dynamic')

    def set_password(self, password):
        self.user_password_hash = generate_password_hash(password)  

    def check_password(self, password):
        return check_password_hash(self.user_password_hash, password)

    # Setting the function to followe user
    def add_to_favorite(self, fpso):
        if not self.is_favorite(fpso):
            self.favorite.append(fpso)

    # Setting up the function to unfollow the user
    def remove_from_favorite(self, fpso):
        if self.is_favorite(fpso):
            self.favorite.remove(fpso)
    
    # Setting up the function which controlos following users
    def is_favorite(self, fpso):
        return self.favorite.filter(favorite.c.fpso_id == fpso.id).count() > 0

    # Setting up the function which returns followed posts
    def favorite_fpso(self):
        favorite_fpsos = Fpso.query.join(favorite, (favorite.c.fpso_id==Fpso.id)).filter(favorite.c.user_id==self.id).order_by(Fpso.fpso_name)
        return favorite_fpsos

    # Reset password function
    def get_reset_password_token(self, expire_in=600):
        return jwt.encode(
            {'reset_password': self.id, 
            'exp': time() + expire_in},
            app.config['SECRET_KEY'], 
            algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id=jwt.decode(token, 
            app.config['SECRET_KEY'], 
            algorithms=['HS256']
            )['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

# SETTING UP THE FPSO MODEL
class Fpso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fpso_owner = db.Column(db.String, index=True, default="None")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    fpso_name = db.Column(db.String, unique=True, index=True)
    fpso_basin = db.Column(db.String, default="None", nullable = True)
    fpso_img_name = db.Column(db.String, default="default_fpso_card")
    fpso_remarks = db.Column(db.String, default="None")
    fpso_psn_lat_deg = db.Column(db.String, nullable = True)
    fpso_psn_lat_min = db.Column(db.String, nullable = True)
    fpso_psn_lat_sec = db.Column(db.String, nullable = True)
    fpso_psn_lat_NS = db.Column(db.String, default="S", nullable = True)
    fpso_psn_long_deg = db.Column(db.String, nullable = True)
    fpso_psn_long_min = db.Column(db.String, nullable = True)
    fpso_psn_long_sec = db.Column(db.String, nullable = True)
    fpso_psn_long_WE = db.Column(db.String, default="W", nullable = True)
    fpso_hdg = db.Column(db.String, nullable = True)
    fpso_disch_rate = db.Column(db.String, nullable = True)
    fpso_vhf = db.Column(db.String, default="None", nullable = True)
    fpso_email_1 = db.Column(db.String, default="fpso@example.com", nullable = True)
    fpso_email_2 = db.Column(db.String, default="fpso@example.com", nullable = True)
    fpso_email_3 = db.Column(db.String, default="fpso@example.com", nullable = True)
    fpso_email_4 = db.Column(db.String, default="fpso@example.com", nullable = True)
    fpso_email_5 = db.Column(db.String, default="fpso@example.com", nullable = True)
    # CARGO
    cargo_name = db.Column(db.String, nullable = True)
    cargo_API = db.Column(db.String, nullable = True)
    cargo_dens = db.Column(db.String, nullable = True)
    cargo_temp = db.Column(db.String, nullable = True)
    cargo_bsw = db.Column(db.String, nullable = True)
    cargo_line_displ_fwd = db.Column(db.String, nullable = True)
    cargo_Hose_Flush_fwd = db.Column(db.String, nullable = True)
    cargo_line_displ_aft = db.Column(db.String, nullable = True)
    cargo_Hose_Flush_aft = db.Column(db.String, nullable = True)
    cargo_info = db.Column(db.String, nullable = True)
    # PRS
    darps_ID_fwd = db.Column(db.String, nullable = True)
    darps_1_tdma_fwd = db.Column(db.String, nullable = True)
    darps_2_tdma_fwd = db.Column(db.String, nullable = True)
    darps_info_fwd = db.Column(db.String, nullable = True)
    darps_1_ts_fwd = db.Column(db.String, nullable = True)
    darps_2_ts_fwd= db.Column(db.String, nullable = True)

    darps_ID_aft = db.Column(db.String, nullable = True)
    darps_1_tdma_aft = db.Column(db.String, nullable = True)
    darps_2_tdma_aft = db.Column(db.String, nullable = True)
    darps_info_aft = db.Column(db.String, nullable = True)
    darps_1_ts_aft = db.Column(db.String, nullable = True)
    darps_2_ts_aft= db.Column(db.String, nullable = True)
    # darps_2_info = db.Column(db.String, nullable = True)
    artemis_address_code_fwd = db.Column(db.String, nullable = True)
    artemis_freq_pair_fwd = db.Column(db.String, nullable = True)
    artemis_info_fwd = db.Column(db.String, nullable = True)
    fanbeam_info_fwd = db.Column(db.String, nullable = True)
    radius_info_fwd = db.Column(db.String, nullable = True)
    
    artemis_address_code_aft = db.Column(db.String, nullable = True)
    artemis_freq_pair_aft = db.Column(db.String, nullable = True)
    artemis_info_aft = db.Column(db.String, nullable = True)
    fanbeam_info_aft = db.Column(db.String, nullable = True)
    radius_info_aft = db.Column(db.String, nullable = True)


    def get_dens_in_15(self):
        dens_at_15 = self.cargo_dens * 15
        return dens_at_15

    def __repr__(self):
        return '<FPSO {}'.format(self.fpso_name)

    
    # Setting up the avatar url
    def avatar(self):
        return "url_for('static', filename='img/{}.jpg').format('default_fpso_card')"
