from flask import render_template, flash, url_for, redirect, request, current_app
from app import db
from app.main import bp
from app.main.forms import EditProfileForm
from flask_login import current_user, login_required
from app.models import User, Movie, People, Character
from datetime import datetime
from math import floor
import json

@bp.route("/")
@login_required
def home():
    return render_template("home.html", title="Home")
  
@bp.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)

@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("main.user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route("/json/<doctype>", methods=['GET'])
@login_required
def api(doctype):
    if doctype == "movies":
        doctype_class = Movie
    elif doctype == "characters":
        doctype_class = Character
    elif doctype == "people":
        doctype_class = People
    else:
        return {'total': 0, 'rows': []}
    search = request.args.get("search", "", type=str)  # full text search
    match = request.args.get("match", None, type=str)  # specific field match
    sort = request.args.get("sort", "", type=str)  # field to sort by
    order = request.args.get("order", None, type=str)  # desc or asc
    offset = request.args.get("offset", 0, type=int)  # start item
    limit = request.args.get("limit", current_app.config["ITEMS_PER_PAGE"], type=int)  # per page
    page = floor(offset / limit) + 1  # estimage page from offset
    filter_ = request.args.get("filter", None, type=str)  #  fields to filter by, not included in search score
    query = {"bool": {}}
    query["bool"]["must"] = []
    if search:
        query["bool"]["must"].append({"multi_match": {"query": search, "fields": ["*"]}})
    if match:
        match_dict = json.loads(match)
        for m in match_dict:
            query["bool"]["must"].append({"match": m})
    # filter options
    if filter_:
        filter_list = json.loads(filter_)
        filters = [{"term": f} for f in filter_list]
        query["bool"]["filter"] = filters
    if not search:
        if not sort or sort not in doctype_class.__searchable__.keys():
            sort = doctype_class.__default_sort__[0]
        else:
            if doctype_class.__searchable__[sort].get('fields',{}).get('raw',{}).get('type','') == 'keyword':
                sort = sort + '.raw'
    if not order or order not in ['asc', 'desc']:
        order = doctype_class.__default_sort__[1]
    items, total = doctype_class.search_query(query, page, limit, sort, order)
    return {'total': total, 'rows': [item.to_dict() for item in items]}