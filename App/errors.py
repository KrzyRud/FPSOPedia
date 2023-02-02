from flask import render_template
from App import app, db

# Custorm 404 error page
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Custorm 500 error page
@app.errorhandler(500)
def internal_errro(error):
    db.session.rollback()
    return render_template('500.html'), 500