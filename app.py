import os

import geocoder

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import lookup, login_required, getLatLong

# initialize flask app
app = Flask(__name__)

# configure session to use the filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# set the database variable to the appropriate database
db = SQL("sqlite:///weather.db")


# Borrowed after_request() from CS50 Finance
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear any possible active sessions
    session.clear()

    if request.method == "POST":
        # Require input from the user
        if not request.form.get("username"):
            flash("Must provide username")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Must provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return render_template("login.html")

        # initialize a session
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    # Clear the user's session and render Login page
    session.clear()
    flash("Logged out")
    return render_template("login.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        # Get user's current location by default using Geocoder
        myLocation = geocoder.ip("me").city.title()

        try:
            forecasts = lookup(myLocation)

        except AttributeError:
            flash("Could not find forecasts for your location")
            return render_template("index.html")

        # current weather
        temp = forecasts["temp"]
        maxtemp = forecasts["maxtemp"]
        mintemp = forecasts["mintemp"]
        # Sunrise and Sunset include dates, but we don't want those, so we only get info from [11] onwards
        sunrise = forecasts["sunrise"][11:]
        sunset = forecasts["sunset"][11:]
        precipitation_chance = forecasts["precipitation_chance"]
        windspeed = forecasts["windspeed"]
        is_day = forecasts["is_day"]

        # 10-day forecast
        maxtemps = forecasts["maxtemps"]
        mintemps = forecasts["mintemps"]
        sunrises = forecasts["sunrises"]
        sunsets = forecasts["sunsets"]
        precipitation_chances = forecasts["precipitation_chances"]

        return render_template(
            "index.html",
            temp=temp,
            maxtemp=maxtemp,
            mintemp=mintemp,
            sunrise=sunrise,
            sunset=sunset,
            precipitation_chance=precipitation_chance,
            windspeed=windspeed,
            is_day=is_day,
            maxtemps=maxtemps,
            mintemps=mintemps,
            sunrises=sunrises,
            sunsets=sunsets,
            precipitation_chances=precipitation_chances,
            location=myLocation,
        )

    else:
        # If user typed in a city in the searchbox
        location = request.form.get("searchbox").title()

        try:
            # lookup user-requested weather info for that city
            forecasts = lookup(location)

        except AttributeError:
            flash("Could not find forecasts for the requested location")
            return render_template("index.html")

        # current weather
        temp = forecasts["temp"]
        maxtemp = forecasts["maxtemp"]
        mintemp = forecasts["mintemp"]
        sunrise = forecasts["sunrise"][11:]
        sunset = forecasts["sunset"][11:]
        precipitation_chance = forecasts["precipitation_chance"]
        windspeed = forecasts["windspeed"]
        is_day = forecasts["is_day"]

        # 10-day forecast
        maxtemps = forecasts["maxtemps"]
        mintemps = forecasts["mintemps"]
        sunrises = forecasts["sunrises"]
        sunsets = forecasts["sunsets"]
        precipitation_chances = forecasts["precipitation_chances"]

        return render_template(
            "index.html",
            temp=temp,
            maxtemp=maxtemp,
            mintemp=mintemp,
            sunrise=sunrise,
            sunset=sunset,
            precipitation_chance=precipitation_chance,
            windspeed=windspeed,
            is_day=is_day,
            maxtemps=maxtemps,
            mintemps=mintemps,
            sunrises=sunrises,
            sunsets=sunsets,
            precipitation_chances=precipitation_chances,
            location=location,
        )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    else:
        # check for blank fields
        if not request.form.get("username") or not request.form.get("password"):
            flash("Fields cannot be blank")
            return render_template("register.html")

        # obtain user inputted info
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        passwordHash = generate_password_hash(password)

        if password != confirmation:
            flash("Passwords don't match")
            return render_template("register.html")

        # check if username has been taken
        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?,?);",
                username,
                passwordHash,
            )

        except ValueError:
            flash("Username taken")
            return render_template("register.html")

        return login()


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    if request.method == "GET":
        return render_template("changepass.html")

    else:
        # Ensure fields are not blank
        if not request.form.get("password") or not request.form.get("new_password"):
            flash("Fields cannot be blank")
            return render_template("changepass.html")

        user_id = session["user_id"]
        oldpassword = request.form.get("password")
        newpassword = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        rows = db.execute("SELECT hash FROM users WHERE id = ?;", user_id)

        currenthash = rows[0]["hash"]

        # Ensure current password is correct
        if not check_password_hash(currenthash, oldpassword):
            flash("Password incorrect")
            return render_template("changepass.html")

        # Ensure new password matches confirmation
        if newpassword != confirmation:
            flash("New password doesn't match confirmation")
            return render_template("changepass.html")

        # generate a new password hash and update our users table
        newhash = generate_password_hash(newpassword)

        db.execute("UPDATE users SET hash = ? WHERE id = ?;", newhash, user_id)

        flash("Password updated")
        return redirect("/")
