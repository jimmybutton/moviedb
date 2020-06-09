from flask import render_template, flash, url_for, redirect, request, current_app
from app import db
from app.main import bp
from app.main.forms import EditProfileForm
from flask_login import current_user, login_required
from app.models import User

@bp.route("/actors")
@login_required
def actors():
    return render_template("actors.html", title="People")
