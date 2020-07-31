from flask import (
    render_template,
    flash,
    url_for,
    redirect,
    request,
    current_app,
    Markup,
    jsonify,
)
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EditMovieForm, DeleteItemForm, SearchForm
from flask_login import current_user, login_required
from app.models import User, Movie
from datetime import datetime
from werkzeug.wrappers import Response
from app.utils import paginate, export_csv
from math import ceil, floor
from sqlalchemy import or_



@bp.route("/movies_json", methods=["GET"])
@login_required
def movies_json():
    search = request.args.get("search", "", type=str)  # full text search
    sort = request.args.get("sort", "", type=str)  # field to sort by
    order = request.args.get("order", "desc", type=str)  # desc or asc
    offset = request.args.get("offset", 0, type=int)  # start item
    limit = request.args.get(
        "limit", current_app.config["ITEMS_PER_PAGE"], type=int
    )  # per page
    page = floor(offset / limit) + 1  # estimage page from offset
    if search:
        # in this case, sort by search score
        movies, total = Movie.search(search, page, limit)
    else:
        if sort not in [i for i in Movie.__dict__.keys() if i[:1] != "_"]:
            sort = "title"
        sort_field = Movie.__dict__[sort]
        order_method = sort_field.desc() if order == "desc" else sort_field.asc()
        movies_query = Movie.query.order_by(order_method).paginate(page, limit, False)
        movies = movies_query.items
        total = movies_query.total
    return {"total": total, "rows": [m.to_dict() for m in movies]}


@bp.route("/directors", methods=["GET"])
@login_required
def unique_directors():
    return jsonify([m.director for m in db.session.query(Movie.director).distinct()])


@bp.route("/movies_old", methods=["GET"])
@login_required
def movies_old():
    searchfields = [
        {"field": "title", "type": "match"},
        {
            "field": "category",
            "type": "select",
            "options": Movie.__fields__["category"]["options"],
        },
        {
            "field": "director",
            "type": "typeahead",
            "url": url_for("main.unique_directors"),
        },
    ]
    sortable = Movie.__sortfields__
    return render_template(
        "movies_old.html",
        title="Movies",
        doctype="movies",
        columns=Movie.__columns__,
        sortable=sortable,
    )


@bp.route("/movies", methods=["GET"])
@login_required
def movies():
    search_form = SearchForm()
    page = request.args.get("page", 1, type=int)
    per_page = 12  # current_app.config["ITEMS_PER_PAGE"]
    if not search_form.validate():
        return redirect('main.movies')
    terms = search_form.q.data
    query = Movie.query
    if terms:
        terms = terms.split(" ")
        for term in terms:
            if not term:
                continue
            query = query.filter(or_(Movie.title.ilike(f"%{term}%"), Movie.plot_summary.ilike(f"%{term}%")))
    movies = query.order_by(Movie.rating_value.desc()).paginate(page, per_page, False)
    # if search:
    #     query = {"bool": {}}
    #     query["bool"]["must"] = []
    #     query["bool"]["must"].append({"multi_match": {"query": search, "fields": ["*"]}})
    #     sort = None
    # else:
    #     query = {
    #         "match_all": {}
    #     }
    #     sort = 'rating_value'
    # order = 'desc'
    # movies, total = Movie.search_query(query, page, limit, sort, order)
    
    # total_pages = ceil(total/limit)
    # pager = SimpleNamespace()
    # pager.page = page
    # pager.per_page = 12
    # pager.total = total
    # pager.next_url = (
    #     url_for("main.movies", page=page+1, q=search) if page < total_pages else None
    # )
    # pager.prev_url = (
    #     url_for("main.movies", page=page-1, q=search) if page > 1 else None
    # )
    # pager.first_url = (
    #     url_for("main.movies", page=1, q=search) if page > 1 else None
    # )
    # pager.last_url = (
    #     url_for("main.movies", page=total_pages, q=search) if page < total_pages else None
    # )
    return render_template(
        "movies.html",
        title="Movies",
        movies=movies,
        search_form=search_form,
    )


@bp.route("/movies/export", methods=["GET"])
@login_required
def movies_export():
    movies = Movie.query.all()
    fields = ["id"] + Movie.__formfields__
    # stream the response as the data is generated
    response = Response(export_csv(movies, fields), mimetype="text/csv")
    # add a filename
    response.headers.set("Content-Disposition", "attachment", filename="movies.csv")
    return response


@bp.route("/movie/<id>")
@login_required
def movie(id):
    movie = Movie.query.get(id)
    if not movie:
        flash("Movie with id={} not found.".format(id))
        return redirect(url_for("main.movies"))
    return render_template("movie.html", movie=movie, title=movie.displayname)


@bp.route("/movie/<id>/cast")
@login_required
def movie_cast(id):
    movie = Movie.query.get(id)
    if not movie:
        flash("Movie with id={} not found.".format(id))
        return redirect(url_for("main.movies"))
    cast = movie.cast.all()
    return {"rows": [c.to_dict() for c in cast]}


@bp.route("/create_movie", methods=["GET", "POST"])
def movie_create():
    form = EditMovieForm()
    if form.validate_on_submit():
        movie = Movie()
        for field in movie.__formfields__:
            form_field = getattr(form, field)
            setattr(movie, field, form_field.data)
        movie.created_by = current_user
        db.session.add(movie)
        db.session.commit()
        flash(
            Markup(
                f"""Movie <a href="{url_for('main.movie', id=movie.id)}">{movie.title}</a> created.""".format()
            )
        )
        if form.submit._value() == "Save and New":
            return redirect(url_for("main.movie_create"))
        else:
            return redirect(url_for("main.movie", id=movie.id))
    return render_template("movie_create.html", title="Create movie", form=form)


@bp.route("/movie/<id>/edit", methods=["GET", "POST"])
@login_required
def edit_movie(id):
    form = EditMovieForm()
    movie = Movie.query.get(id)
    if not movie:
        flash("Movie with id={} not found.".format(id))
        return redirect(url_for("movies"))
    if form.validate_on_submit():
        for field in movie.__formfields__:
            form_field = getattr(form, field)
            setattr(movie, field, form_field.data)
        movie.modified_by = current_user
        db.session.add(movie)
        db.session.commit()
        flash(
            Markup(
                f"""Movie <a href="{url_for('main.movie', id=movie.id)}">{movie.title}</a> updated.""".format()
            )
        )
        return redirect(url_for("main.movie", id=movie.id))
    elif request.method == "GET":
        for field in movie.__formfields__:
            getattr(form, field).data = getattr(movie, field)

    return render_template("movie_create.html", form=form, movie=movie)


@bp.route("/movie/<id>/delete", methods=["GET", "POST"])
@login_required
def delete_movie(id):
    form = DeleteItemForm()
    movie = Movie.query.get(id)
    if not movie:
        flash("Movie with id={} not found.".format(id))
        return redirect(url_for("main.movies"))
    if form.validate_on_submit():
        title = movie.title
        db.session.delete(movie)
        db.session.commit()
        flash("Movie {} ({}) has been deleted.".format(movie.title, movie.year))
        return redirect(url_for("main.movies"))
    return render_template("movie_delete.html", form=form, movie=movie)
