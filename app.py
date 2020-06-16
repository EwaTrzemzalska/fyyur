#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from sqlalchemy import distinct
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Shows', backref='venue',
                            cascade="all, delete-orphan")

    def __repr__(self):
        return f"<id={self.id}, name={self.name}, city={self.city}>"


class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_venues = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Shows', backref='artist',
                            cascade="all, delete-orphan")


class Shows(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []

    # get tuples of city and state
    all_locations = Venue.query.with_entities(
        Venue.city, Venue.state).distinct().all()

    for location in all_locations:
        original_venues = Venue.query.filter_by(city=location[0]).all()
        venues = []

        for venue in original_venues:
            venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(Shows.query.filter_by(id=venue.id).filter(Shows.start_time > datetime.now()).all())
            })

        data.append({
            "city": location[0],
            "state": location[1],
            "venues": venues
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    search_term = request.form.get('search_term')
    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    data = []

    for result in results:
        data.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len(Shows.query.filter_by(id=result.id).filter(Shows.start_time > datetime.now()).all())
        })

    response = {
        "count": len(results),
        "data": data
    }

    print(result)
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    all_past_shows = Shows.query.filter_by(venue_id=venue_id).filter(
        Shows.start_time < datetime.now()).all()
    all_upcoming_shows = Shows.query.filter_by(venue_id=venue_id).filter(
        Shows.start_time > datetime.now()).all()
    past_shows = []
    upcoming_shows = []

    # add past shows details
    for show in all_past_shows:
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })

    # add upcoming shows details
    for show in all_upcoming_shows:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


def create_venue_from_request(request):
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    website = request.form['website']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    if 'seeking_talent' in request.form:
        seeking_talent = True
    else:
        seeking_talent = False
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, website=website,
                  image_link=image_link, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    return venue


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue = create_venue_from_request(request)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    all_artists = Artist.query.all()

    for artist in all_artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    search_term = request.form.get('search_term')
    results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    data = []

    for result in results:
        data.append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len(Shows.query.filter_by(id=result.id).filter(Shows.start_time > datetime.now()).all())
        })

    response = {
        "count": len(results),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    all_past_shows = Shows.query.filter_by(artist_id=artist_id).filter(
        Shows.start_time < datetime.now()).all()
    all_upcoming_shows = Shows.query.filter_by(artist_id=artist_id).filter(
        Shows.start_time > datetime.now()).all()
    past_shows = []
    upcoming_shows = []

    # add past shows details
    for show in all_past_shows:
        past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        })

    # add upcoming shows details
    for show in all_upcoming_shows:
        upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venues": artist.seeking_venues,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)

    if artist:
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.image_link.data = artist.image_link
        form.website.data = artist.website
        form.seeking_venues.data = artist.seeking_venues
        form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    artist = Artist.query.get(artist_id)
    original_name = artist.name

    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website']
        if 'seeking_venues' in request.form:
            artist.seeking_venues = True
        else:
            artist.seeking_venues = False
        artist.seeking_description = request.form['seeking_description']

        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + artist.name + ' was successfully updated!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +
              original_name + ' could not be updated.')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    if venue:
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.address.data = venue.address
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.website.data = venue.website
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    venue = Venue.query.get(venue_id)
    original_name = venue.name

    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website']
        if 'seeking_talent' in request.form:
            venue.seeking_talent = True
        else:
            venue.seeking_talent = False
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully updated!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              original_name + ' could not be updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


def create_artist_from_request(request):
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    website = request.form['website']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    if 'seeking_venues' in request.form:
        seeking_venues = True
    else:
        seeking_venues = False
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, website=website, image_link=image_link,
                    facebook_link=facebook_link, seeking_venues=seeking_venues, seeking_description=seeking_description)
    return artist


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    # called upon submitting the new artist listing form
    try:
        artist = create_artist_from_request(request)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    data = []
    all_shows = Shows.query.all()

    for show in all_shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    return render_template('pages/shows.html', shows=data)


# Create Show
# -----------------------------------------------------------------

def create_show_from_request(request):
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Shows(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    return show


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    # called to create new shows in the db, upon submitting new show listing form
    try:
        show = create_show_from_request(request)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')

# -----------------------------------------------------------------


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
