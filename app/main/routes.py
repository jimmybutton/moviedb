from flask import render_template, flash, url_for, redirect, request, current_app, Markup
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EditMovieForm, DeleteItemForm, SearchForm
from flask_login import current_user, login_required
from app.models import User, Movie
from datetime import datetime
import csv
from io import StringIO
from werkzeug.wrappers import Response
from app.utils import paginate
from math import ceil, floor


@bp.route("/")
@login_required
def home():
    return render_template("home.html", title="Dashboard")

@bp.route("/movies_json", methods=['GET'])
@login_required
def movies_json():
    search = request.args.get("search", "", type=str)  # full text search
    sort = request.args.get("sort", "", type=str)  # field to sort by
    order = request.args.get("order", "desc", type=str)  # desc or asc
    offset = request.args.get("offset", 0, type=int)  # start item
    limit = request.args.get("limit", current_app.config["ITEMS_PER_PAGE"], type=int)  # per page
    page = floor(offset / limit) + 1  # estimage page from offset
    if search:
        # in this case, sort by search score
        movies, total = Movie.search(search, page, limit)
    else:
        if sort not in [i for i in Movie.__dict__.keys() if i[:1] != '_']:
            sort = "rating_value"
        sort_field = Movie.__dict__[sort]
        order_method = sort_field.desc() if order == "desc" else sort_field.asc()
        movies_query = Movie.query.order_by(order_method).paginate(
            page, limit, False
        )
        movies = movies_query.items
        total = movies_query.total
    return {'total': total, 'rows': [m.to_dict() for m in movies]}




@bp.route("/movies", methods=['GET'])
@login_required
def movies():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", current_app.config["ITEMS_PER_PAGE"], type=int)
    order_by = request.args.get("order_by", "rating_value", type=str)
    sort = request.args.get("sort", "desc", type=str)
    q = request.args.get("q", "", type=str)
    if q:
        movies, total = Movie.search(q, page, per_page)
        movies.items = movies
        movies.page = page
        movies.per_page = per_page
        movies.total = total
        movies.has_next = True if total > page * per_page else False
        movies.has_prev = True if page > 1 else False
        movies.pages = ceil(total / per_page)
    else:
        if order_by not in [i for i in Movie.__dict__.keys() if i[:1] != '_']:
            order_by = "rating_value"
        order_by_field = Movie.__dict__[order_by]
        order_method = order_by_field.desc() if sort == "desc" else order_by_field.asc()
        movies = Movie.query.order_by(order_method).paginate(
            page, per_page, False
        )
    search_form = SearchForm()
    next_url = url_for("main.movies", page=page-1, order_by=order_by, sort=sort, q=q) if movies.has_next else None
    prev_url = url_for("main.movies", page=page+1, order_by=order_by, sort=sort, q=q) if movies.has_prev else None
    pages = [{'page': p, 'url': url_for("main.movies", page=p, order_by=order_by, sort=sort, q=q)} for p in paginate(current_page=page, total_pages=movies.pages, num_links=5)]
    return render_template(
        "movies.html",
        title="Movies",
        movies=movies,
        search_form=search_form,
        next_url=next_url,
        prev_url=prev_url,
        order_by=order_by,
        sort=sort,
        pages=pages
    )


@bp.route("/movies/export", methods=['GET'])
@login_required
def movies_export():
    def generate(movies):
        """
        Generate the data with csv.writer and stream the response. 
        Use StringIO to write to an in-memory buffer rather than 
        generating an intermediate file.
        """
        data = StringIO()
        w = csv.writer(data)

        # write header
        w.writerow(('title', 'year', 'description', 'stars'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # write each log item
        for movie in movies:
            w.writerow((
                movie.title,
                movie.year,
                movie.description,
                movie.stars
            ))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    order_by = request.args.get("order_by", "title", type=str)
    sort = request.args.get("sort", "asc", type=str)
    if order_by not in [i for i in Movie.__dict__.keys() if i[:1] != '_']:
        order_by = "title"
    order_by_field = Movie.__dict__[order_by]
    order_method = order_by_field.desc() if sort == "desc" else order_by_field.asc()
    movies = Movie.query.order_by(order_method).all()
    
    # stream the response as the data is generated
    response = Response(generate(movies), mimetype='text/csv')
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
    return render_template("movie.html", movie=movie, title="Movies")


@bp.route("/create_movie", methods=["GET", "POST"])
def movie_create():
    form = EditMovieForm()
    if form.validate_on_submit():
        movie = Movie()
        # for k,v in form.__dict__.items():
        #     if not k.startswith('_') and k not in ['meta', 'submit', 'csrf_token']:
        #         if v.data:
        #             movie.__dict__[k] = v.data
        movie.title = form.title.data 
        movie.year = form.year.data 
        movie.certificate = form.certificate.data
        movie.category = form.category.data
        movie.release_date = form.release_date.data
        movie.plot_summary = form.plot_summary.data
        movie.director = form.director.data
        movie.rating_value = form.rating_value.data
        movie.rating_count = form.rating_count.data 
        movie.poster_url = form.poster_url.data
        movie.runtime = form.runtime.data 
        movie.url = form.url.data

        movie.created_by = current_user
        db.session.add(movie)
        db.session.commit()
        flash(Markup(f"""Movie <a href="{url_for('main.movie', id=movie.id)}" class="inline-link">{movie.title}</a> created.""".format()))
        if form.submit._value() == 'Create and New':
            return redirect(url_for("main.movie_create"))
        else:
            return redirect(url_for("main.movie", id=movie.id))
    return render_template("movie_create.html", form=form)


@bp.route("/movie/<id>/edit", methods=["GET", "POST"])
@login_required
def edit_movie(id):
    form = EditMovieForm()
    movie = Movie.query.get(id)
    if not movie:
        flash("Movie with id={} not found.".format(id))
        return redirect(url_for("movies"))
    if form.validate_on_submit():
        # for k,v in form.__dict__.items():
        #     if not k.startswith('_') and k not in ['meta', 'submit', 'csrf_token']:
        #         if v.data:
        #             movie.__dict__[k] = v.data
        movie.title = form.title.data 
        movie.year = form.year.data 
        movie.certificate = form.certificate.data
        movie.category = form.category.data
        movie.release_date = form.release_date.data
        movie.plot_summary = form.plot_summary.data
        movie.director = form.director.data
        movie.rating_value = form.rating_value.data
        movie.rating_count = form.rating_count.data 
        movie.poster_url = form.poster_url.data
        movie.runtime = form.runtime.data 
        movie.url = form.url.data

        movie.modified_by = current_user
        db.session.add(movie)
        db.session.commit()
        flash("Movie {} has been updated.".format(movie.title))
        return redirect(url_for("main.movie", id=movie.id))
    elif request.method == "GET":
        # for k,v in movie.__dict__.items():
        #     if not k.startswith('_') and k not in ['id', 'created_by', 'created_id', 'created_timestamp', 'modified_by', 'modified_id', 'modified_timestamp']:
        #         form.__dict__[k].data = v
        form.title.data = movie.title
        form.year.data = movie.year 
        form.certificate.data = movie.certificate
        form.category.data = movie.category
        form.release_date.data = movie.release_date
        form.plot_summary.data = movie.plot_summary
        form.director.data = movie.director
        form.rating_value.data = movie.rating_value
        form.rating_count.data = movie.rating_count 
        form.poster_url.data = movie.poster_url
        form.runtime.data = movie.runtime 
        form.url.data = movie.url

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


@bp.route("/actors")
@login_required
def actors():
    return render_template("actors.html", title="People")


@bp.route("/users")
@login_required
def users():
    users = User.query.all()
    return render_template("users.html", title="Users", users=users)


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