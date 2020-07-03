from flask import render_template, flash, url_for, redirect, request, current_app
from app import db
from app.main import bp
from app.main.forms import EditProfileForm
from flask_login import current_user, login_required
from app.models import User, People
from math import floor

@bp.route("/people_json", methods=['GET'])
@login_required
def people_json():
    search = request.args.get("search", "", type=str)  # full text search
    sort = request.args.get("sort", "", type=str)  # field to sort by
    order = request.args.get("order", "desc", type=str)  # desc or asc
    offset = request.args.get("offset", 0, type=int)  # start item
    limit = request.args.get("limit", current_app.config["ITEMS_PER_PAGE"], type=int)  # per page
    page = floor(offset / limit) + 1  # estimage page from offset
    if search:
        # in this case, sort by search score
        people, total = People.search(search, page, limit)
    else:
        if sort not in [i for i in People.__dict__.keys() if i[:1] != '_']:
            sort = "name"
        sort_field = People.__dict__[sort]
        order_method = sort_field.desc() if order == "desc" else sort_field.asc()
        query = People.query.order_by(order_method).paginate(
            page, limit, False
        )
        people = query.items
        total = query.total
    return {'total': total, 'rows': [p.to_dict() for p in people]}


@bp.route("/people", methods=['GET'])
@login_required
def people():
    return render_template("people.html", title="People")


@bp.route("/person/<id>")
@login_required
def person(id):
    person = People.query.get(id)
    if not person:
        flash("Person with id={} not found.".format(id))
        return redirect(url_for("main.people"))
    return render_template("person.html", person=person, title=person.name)

