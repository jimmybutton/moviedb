from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, DecimalField, SelectField, DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, NumberRange, Optional
from app.models import User
from datetime import date
from flask import request


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
    
class EditMovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = SelectField('Year', validators=[DataRequired()], choices=[(y, y) for y in range(int(date.today().year), 1900, -1)], coerce=int)
    certificate = SelectField('Certificate', choices=[('',''),('U','U'),('12','12'),('12A','12A'),('15','15'),('18','18'),('R18','R18'),('A','A'),('PG','PG'),('U/A','U/A'),('S','S'),('X','X')])
    category = SelectField('Category', choices=[('',''),('Action','Action'),('Adventure','Adventure'),('Animation','Animation'),('Biography','Biography'),('Comedy','Comedy'),('Crime','Crime'),('Drama','Drama'),('Film-Noir','Film-Noir'),('Horror','Horror'),('Mystery','Mystery'),('Western','Western')])
    release_date = StringField('Release date')
    director = StringField('Director', validators=[DataRequired()])
    plot_summary = TextAreaField('Plot summary', validators=[Length(min=0, max=300)])
    rating_value = DecimalField(label='Rating', validators=[Optional(), NumberRange(min=0, max=10)])
    rating_count = IntegerField(label='Rating count', validators=[Optional(), NumberRange(min=0)])
    runtime = IntegerField(label='Runtime (min)', validators=[Optional()])
    poster_url = StringField('Poster URL')
    url = StringField('URL')
    submit = SubmitField('Save')
    submit_and_new = SubmitField('Save and New')

    # def validate_year(self, year):
    #     min_year = 1800
    #     max_year = date.today().year
    #     if year.data < min_year or year.data > max_year:
    #         raise ValidationError('Please use a year between {} and {}.'.format(min_year, max_year))
    
    # def validate_stars(self, stars):
    #     if stars.data < 0 or stars.data > 10:
    #         raise ValidationError('Please use a number between 0 and 10.')

class EditPersonForm(FlaskForm):
    name = StringField('Name')
    birthname = StringField('Birthname')
    dob = DateField('Date of Birth', format='%d/%m/%Y')
    height = StringField('Height')
    bio = TextAreaField('Biographie')
    url = StringField('URL')
    image_url = StringField('Image URL')
    submit = SubmitField('Save')
    submit_and_new = SubmitField('Save and New')

class DeleteItemForm(FlaskForm):
    submit = SubmitField('Delete')

class SearchForm(FlaskForm):
    q = StringField('Search')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
    