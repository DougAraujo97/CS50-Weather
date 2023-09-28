<div align="center">
    <h1 id="title">CS50 Weather</h1>
</div>

<br>
<div align="center" id="links">
    &#9734;&nbsp;&nbsp;<a href="#video">Video Demo</a>&nbsp;&nbsp;
    <a href="#description">Description</a>&nbsp;&nbsp;
    <a href="#origins">How it Began</a>&nbsp;&nbsp;
    <a href="#helpers">Helpers</a>&nbsp;&nbsp;
    <a href="#back_end">Back-End</a>&nbsp;&nbsp;
    <a href="#front_end">Front-End</a>&nbsp;&nbsp;
    <a href="#closer">Final Thoughts</a>&nbsp;&nbsp;&#9734;
</div>

<br>
<h2 id="video">Video Demonstration</h2>

[Demo on YouTube](https://youtu.be/wHC4IaeaE5c)

<h2 id="description">Description</h2>

Welcome to CS50 Weather, a simple weather application you can use to find the current temperature, highs & lows, sunrise & sunset times and the chance of precipitation for the current date, the next 5 days or the next 10 days, anywhere in the world!

<h2 id="origins">How it all started</h2>

The idea for this app came about because I was thinking about the weather during the insane heat wave we all faced in July 2023. I wanted to challenge myself to build a weather app where the forecasts were displayed on cards that were animated to fan out like a deck of playing cards depending on the amount of days the user wanted to look up. Before I even sat down and started coding I began to think through the app's design both on the front and back-end because I didn't want to do something too easy for this project. I began to question how I'd get the weather data. Would I be skilled enough to animate the cards? Would I want users to create accounts and sign in? What would I include in the database? Would I let users change their passwords? Would I allow them to save their home address or would I show them the forecast for their current position by default? What colors would I use? Upon realizing I had more questions than answers, I decided this would be a large enough challenge to tackle for my final project.

<h2 id="helpers">Helpers.py</h2>

***helpers.py*** is a file containing 3 functions that ***app.py*** references: *login_required(), getLatLong()* and *lookup()*.

***login_required()*** redirects a user to the login page if the user doesn't currently have an active session.

```Python

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

```

<br>

***getLatLong()*** takes a city name as an argument and utilizes the [Nominatim](https://nominatim.org/) API to get latitude and longitude coordinates for said city. The function will raise an **AttributeError** if coordinates for that city cannot be located.

```Python

def getLatLong(city):
    try:
        geolocator = Nominatim(user_agent="MyApp")

        location = geolocator.geocode(city)

        lat = location.latitude
        long = location.longitude

        return lat, long

    except AttributeError:
        raise AttributeError

```

<br>

***lookup()*** also takes a city name as an argument. It calls ***getLatLong()*** to get the latitude and longitude coordinates for the requested city and then it queries the [Open-Meteo](https://open-meteo.com/en/docs) weather API to get forecast data for up to 14 days. The coordinates are necessary because they get added to the request URL when querying the API. The function converts the API response to a **JSON** format so it can be indexed into. Variables are then assigned for the current day's forecast, including temperature, sunrise, sunset, chance of precipitation, windspeed and time-of-day information. Afterwards, lists are created containing the forecasts of the remaining 13 days. The lists are then reversed so the forecast data goes from least to most current, so that when the cards with the forecasts are rendered in *index.html*, the more-current forecasts get stacked on top of the least-current. The first 4 items in each list are then deleted, because this app displays 10-day forecasts, not 14-day forecasts, and **Open-Meteo** only offers 7-day or 14-day forecasts. Finally, the function returns the current-day forecast variables and the 10-day forecast lists.

```Python

def lookup(city):
    lat, long = getLatLong(city)

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={long}"
        f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max"
        f"&current_weather=true&timezone=auto&forecast_days=14"
    )

    response = requests.get(url).json()

    temp = int(response["current_weather"]["temperature"])
    maxtemp = int(response["daily"]["temperature_2m_max"][0])
    mintemp = int(response["daily"]["temperature_2m_min"][0])
    sunrise = response["daily"]["sunrise"][0]
    sunset = response["daily"]["sunset"][0]
    precipitation_chance = response["daily"]["precipitation_probability_max"][0]
    windspeed = int(response["current_weather"]["windspeed"])
    is_day = response["current_weather"]["is_day"]

    maxtemps = [int(i) for i in response["daily"]["temperature_2m_max"]]
    mintemps = [int(i) for i in response["daily"]["temperature_2m_min"]]
    sunrises = [i for i in response["daily"]["sunrise"]]
    sunsets = [i for i in response["daily"]["sunset"]]
    precipitation_chances = [
        i for i in response["daily"]["precipitation_probability_max"]
    ]

    maxtemps.reverse()
    mintemps.reverse()
    sunrises.reverse()
    sunsets.reverse()
    precipitation_chances.reverse()

    del maxtemps[0:4]
    del mintemps[0:4]
    del sunrises[0:4]
    del sunsets[0:4]
    del precipitation_chances[0:4]

    return {
        "temp": temp,
        "maxtemp": maxtemp,
        "mintemp": mintemp,
        "sunrise": sunrise,
        "sunset": sunset,
        "precipitation_chance": precipitation_chance,
        "windspeed": windspeed,
        "is_day": is_day,
        "maxtemps": maxtemps,
        "mintemps": mintemps,
        "sunrises": sunrises,
        "sunsets": sunsets,
        "precipitation_chances": precipitation_chances,
    }

```

<br>
<h2 id="back_end">Back-End</h2>

**app.py** contains 6 functions that control this application and how the user is allowed to interact with it: ***after_request(), login(), logout(), index(), register() and changepass().*** Before executing any of those functions, it imports: **geocoder**, *SQL* from the **CS50** library, *Flask, flash, redirect, render_template, request* and *session* from the **flask** library, *Session* from the **flask_session** library, *mkdtemp* from the **tempfile** library, *check_password_hash* and *generate_password_hash* from the **werkzeug.security** library, and finally, *lookup, getLatLong* and *login_required* from **helpers.py**.

```Python

import geocoder

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import lookup, login_required, getLatLong

```

<br>

After importing the functions it needs, **app.py** initializes itself as a Flask app, configures Session to use the computer's filesystem and assigns the app's sqlite database to the ***db*** variable.

```Python

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///weather.db")

```

<br>

***after_request()*** takes a response as an argument and ensures that response isn't cached by modifying the ***Cache-Control, Expires*** and ***Pragma*** response headers. It sets ***Cache-Control*** to *no-cache, no-store, must-revalidate*, ***Expires*** to 0 and ***Pragma*** to *no-cache*, and finally, returns the response.

```Python

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

```

<br>

***login()*** takes no arguments and is called whenever the user requests the */login* route either via ***GET*** or via ***POST***. If the user requests the route via ***GET***, then *login.html* is rendered via ***render_template()***. Otherwise, any current sessions that may be active are cleared and the function checks for valid user input. The *username* and *password* fields cannot be empty and the inputted password is checked against the password hash stored in the *users* table in the ***weather.db*** database by calling ***check_password_hash()***. If any of the inputs are invalid, the corresponding error message will be flashed onscreen by calling ***flash()*** and the user will be prompted to input their information again. Once all inputs are valid, a session is initialized for that user's ID and the user is redirected to the */* route.

```Python

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            flash("Must provide username")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Must provide password")
            return render_template("login.html")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")

```

<br>

***logout()*** requires the user to be logged in, takes no arguments and is called whenever the user requests the */logout* route. The function clears the user's current active session, flashes a message onscreen confirming to the user that they've been logged out, and redirects the user to */login*.

```Python

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out")
    return render_template("login.html")

```

<br>

***index()*** requires the user to be logged in, takes no arguments and is called whenever the user requests the */* route either via ***GET*** or ***POST***. If the request method is ***GET***, then *Geocoder* will get the user's city based on their IP address and call ***lookup()*** to get a *forecasts* variable for that location to present to the user. The function will index into *forecasts* and assign different variables for the different information the ***lookup()*** function returned. Sunrise and Sunset data is indexed into from the 11th position onwards, since all we want is the time of the sunrise and sunset, not the date. Once all the relevant variables are assigned, they are all sent to *index.html* where there are placeholders awaiting the information. The same thing happens if the request method is ***POST***, with the sole difference being that the *location* variable is assigned based on the user's input into the searchbox instead of getting their location via their IP address.

```Python

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        myLocation = geocoder.ip("me").city.title()

        try:
            forecasts = lookup(myLocation)

        except AttributeError:
            flash("Could not find forecasts for your location")
            return render_template("index.html")

        temp = forecasts["temp"]
        maxtemp = forecasts["maxtemp"]
        mintemp = forecasts["mintemp"]
        sunrise = forecasts["sunrise"][11:]
        sunset = forecasts["sunset"][11:]
        precipitation_chance = forecasts["precipitation_chance"]
        windspeed = forecasts["windspeed"]
        is_day = forecasts["is_day"]

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
        location = request.form.get("searchbox").title()

        try:
            forecasts = lookup(location)

        except AttributeError:
            flash("Could not find forecasts for the requested location")
            return render_template("index.html")

        temp = forecasts["temp"]
        maxtemp = forecasts["maxtemp"]
        mintemp = forecasts["mintemp"]
        sunrise = forecasts["sunrise"][11:]
        sunset = forecasts["sunset"][11:]
        precipitation_chance = forecasts["precipitation_chance"]
        windspeed = forecasts["windspeed"]
        is_day = forecasts["is_day"]

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

```

<br>

***register()*** takes no arguments and is called whenever the user requests the */register* route either via ***GET*** or ***POST***. If the request method is ***GET***, the *register.html* template will be rendered for the user. Otherwise, the function will check for valid user input. If any input fields are blank, or the password doesn't match the password confirmation, or the username has already been taken, the corresponding error message will be flashed onscreen and the user will be directed back to *register.html*. If all inputs are valid, the user's new username and password hash are added to the *users* table in ***weather.db*** and they are logged in automatically by calling ***login()***.

```Python

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    else:
        if not request.form.get("username") or not request.form.get("password"):
            flash("Fields cannot be blank")
            return render_template("register.html")

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        passwordHash = generate_password_hash(password)

        if password != confirmation:
            flash("Passwords don't match")
            return render_template("register.html")

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

```

<br>

***changepass()*** takes no arguments and is called whenever the user requests the */changepass* route either via ***GET*** or ***POST***. If the request method is ***GET***, the *changepass.html* template will be rendered for the user. Otherwise, the function will check for valid user input. If any input fields are blank, or the user gets their current password incorrect, or the password doesn't match the password confirmation, the corresponding error message will be flashed onscreen and the user will be directed back to *changepass.html*. If all inputs are valid, the user's password hash is updated in the *users* table in ***weather.db*** and they are redirected to *index.html*, where a message will flash onscreen to confirm their password has changed.

```Python

@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    if request.method == "GET":
        return render_template("changepass.html")

    else:
        if not request.form.get("password") or not request.form.get("new_password"):
            flash("Fields cannot be blank")
            return render_template("changepass.html")

        user_id = session["user_id"]
        oldpassword = request.form.get("password")
        newpassword = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        rows = db.execute("SELECT hash FROM users WHERE id = ?;", user_id)

        currenthash = rows[0]["hash"]

        if not check_password_hash(currenthash, oldpassword):
            flash("Password incorrect")
            return render_template("changepass.html")

        if newpassword != confirmation:
            flash("New password doesn't match confirmation")
            return render_template("changepass.html")

        newhash = generate_password_hash(newpassword)

        db.execute("UPDATE users SET hash = ? WHERE id = ?;", newhash, user_id)

        flash("Password updated")
        return redirect("/")

```

<br>

Finally, for this app's back-end, there is the ***SQLITE*** database, *weather.db*, containing a singular *users* table that includes a user's ID, username and password hash. I included a file called ***weather.sql*** because that is where I wrote and formatted the code to create the table. The users' IDs will increment automatically as they register and neither the username nor the hash columns can be NULL.

```sql

CREATE TABLE
    users (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username TEXT NOT NULL,
        hash TEXT NOT NULL
    );

```

<br>

<h2 id="front_end">Front-End</h2>

The ***templates*** folder contains 5 html pages that the user can be directed to based on their interactions with this app: *layout.html, register.html, login.html, index.html* and *changepass.html*. Also crucial to this app's front-end is the ***static*** folder which includes two background images: *background.jpg* and *background_night.jpg*, 2 icons for the app: *icons8-weather-bubbles-16.png* which is 16 pixels wide and is displayed in the browser tab, and *icons8-weather-bubbles-120.png* which is 120 pixels wide and is displayed in the app's navbar, a stylesheet: *styles.css* and all the ***JavaScript*** for our app in *script.js*.

<br>

***layout.html*** contains the base html template for the app, meaning all 4 other pages will merely extend this page with Jinja. In the *head* tag, the *meta* tags specify the charset to "utf-8" and make the app mobile-friendly by setting the viewport width to the width of whichever device is being used. The *link* tags set *styles.css* and [Bootstrap's](https://getbootstrap.com/) CSS as the app's stylesheets and import *icons8-weather-bubbles-16.png* as the app's icon. The *script* tags import ***JavaScript*** from Bootstrap, *script.js* and [FontAwesome](https://fontawesome.com/), which will make the app both pleasant to look at and more interactive. Finally, the *title* tag specifies the title that will display on the browser tab as "CS50 Weather:" and the rest of the title gets set depending on which specific html page is being rendered.

```html

<head>

    <meta charset="utf-8">
    <meta name="viewport" content="initial-scale=1, width=device-width">

    <link crossorigin="anonymous" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" rel="stylesheet">

    <link href="static/icons8-weather-bubbles-16.png" rel="icon">

    <link href="/static/styles.css" rel="stylesheet">

    <script crossorigin="anonymous" src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p">
    </script>

    <script src="static/script.js"></script>

    <script src="https://kit.fontawesome.com/9fb6857f30.js" crossorigin="anonymous"></script>

    <title>CS50 Weather: {% block title %}{% endblock %}</title>

</head>

```

<br>

The *body* tags contain all the html that actually gets rendered to the user. The first tag is a ***span*** whose ID is *#is_day* and it contains a Jinja placeholder, *{{is_day}}* as an attribute that gets assigned based on whether or not the sun has set wherever the user is looking up a forecast. The attribute will be a 1 if the sun has not set, and a 0 if it has. The code in ***script.js*** will target this span based on its ID and check the *is_day* attribute to render the correct background and color scheme for the page based on the time of day. Next is the *nav* tags, containing the app's navbar. The Navbar consists of the app's logo: *icons8-weather-bubbles-120.png* and a header that reads "CS50 Weather". Depending on whether or not the user has logged in, the navbar will also either display two tabs: *register* and *login*, or 3 tabs: *Today, 5-day forecast* and *10-day forecast*. If the latter is true, the navbar will also contain a dropdown menu: *Account*, which offers control over the temperature units: *C°* and *F°*, the options to *Change password* and *Log Out*, and finally, a searchbar the user can interact with to look up forecasts. This navbar will collapse into an icon found on [FontAwesome](https://fontawesome.com/) on smaller screens, and when that icon is clicked, the remaining items on the navbar will be displayed in a dropdown menu. Next, the app checks for flashed messages, and if there are any, they will be displayed in a header directly underneath the Navbar. The *main* tags are empty in ***layout.html***, but these are what all the other html pages will extend with whatever needs to be displayed next. Finally, the document contains *footer* tags crediting [Icons8](https://icons8.com) for the app's icon and logo.

```html

<body>
    <span id="is_day" {{ is_day }}></span>

    <nav class="nav navbar navbar-expand-lg" id="navbar">
        <div class="container-fluid">
            <a href="/" class="logo navbar-brand">
                <img src="static/icons8-weather-bubbles-120.png" alt="logo for the app consisting of a sun hidden behind a cloud surrounded by multicolored bubbles">
                <h4>CS50 Weather</h4>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarTogglerDemo02" aria-controls="navbarTogglerDemo02" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon">
                    <i class="fas fa-bars"></i>
                </span>
            </button>
            <div class="collapse navbar-collapse" id="navbarTogglerDemo02">
                <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
                    {% if session["user_id"] %}
                        <li class="nav-item">
                            <a class="nav-link button" id="today">Today</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link button" id="five_day">5-Day Forecast</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link button" id="ten_day">10-Day Forecast</a>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" data-bs-toggle="dropdown" href="#" role="button" aria-expanded="false">Account</a>
                            <ul class="dropdown-menu mb-2">
                                <li><a class="dropdown-item button" id="celsius">C°</a></li>
                                <li><a class="dropdown-item button" id="fahrenheit">F°</a></li>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li><a class="dropdown-item" href="/changepass">Change Password</a></li>
                                <li><a class="dropdown-item" href="/logout">Log Out</a></li>
                            </ul>
                        </li>
                        <li>
                            <form action="/" method="post">
                                <input autocomplete="off" autofocus class="form-control mx-auto w-auto" name="searchbox" placeholder="City, State, Country" type="text">
                            </form>
                        </li>
                    {% else %}
                        <li class="nav-item ms-auto">
                            <a class="nav-link" href="/register">Register</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/login">Login</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    {% if get_flashed_messages() %}
        <header>
            <div class="alert alert-info mb-0 text-center" role="alert">
                {{ get_flashed_messages() | join(" ") }}
            </div>
        </header>
    {% endif %}

    <main class="container-fluid py-5 text-center">
        {% block main %}{% endblock %}
    </main>

    <footer class="text-center">
        <div class="footer">
            <a target="_blank" href="https://icons8.com/icon/zJJ51w5xgKWA/weather">Weather</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>
        </div>
    </footer>

</body>

```

<br>

***register.html*** extends the *main* tags in ***layout.html*** with: a title that reads "Register", 3 input fields for a username, password and password confirmation, respectively, and a button that reads "Register" and submits the form to */register*. ***app.py*** will target each individual form based on its *name* attribute.

```html

{% extends "layout.html" %}

{% block title %}
    Register
{% endblock %}

{% block main %}
    <div class="mx-auto mb-3">
        <p class="location">Register</p>
    </div>
    <form action="/register" method="post">
        <div class="mb-3">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto" id="username" name="username" placeholder="Username" type="text">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" id="password" name="password" placeholder="Password" type="password">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" id="confirmation" name="confirmation" placeholder="Confirm Password" type="password">
        </div>
        <button class="btn btn-primary" type="submit">Register</button>
    </form>
{% endblock %}

```

<br>

***login.html*** is the same as ***register.html*** in every way, with the exceptions being the title on the browser tab, the title on the page which now reads "Welcome", the lack of a password confirmation field and the button now reading "login" and submitting the form to */login*.

```html

{% extends "layout.html" %}

{% block title %}
    Login
{% endblock %}

{% block main %}
    <div class="mx-auto mb-3">
        <p class="location">Welcome</p>
    </div>
    <form action="/login" method="post">
        <div class="mb-3">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto" id="username" name="username" placeholder="Username" type="text">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" id="password" name="password" placeholder="Password" type="password">
        </div>
        <button class="btn btn-primary" type="submit">Log In</button>
    </form>
{% endblock %}

```

<br>

***index.html*** is this app's main page where the forecasts are displayed. Its browser tab will read "CS50 Weather: Home" and the title onscreen will be whatever location's forecast is being presented. The main focus of this page are the cards which contain the forecasts. They are wrapped in a ***div*** with a class of *cards*, and each subsequent card is a ***div*** in and of itself containing a class of *card* and a ***ul*** with that date's forecast. Every card also has 5 containers: *total_info_container, info_container, temp_container, sunrise_container* and *additional_info_container* that each hold different forecast information, and this was done as a styling choice to present the information on different sections of the card. The cards' classes and IDs will be targeted by CSS and JavaScript to style and animate them according to the user's interaction with the page. The first card which will always be displayed onscreen contains the current forecast. It has a class of *current_forecast* and an ID of *today_card*. Every temperature and its unit displayed on the card is wrapped in an individual ***span*** with the class *temp* and *temp_unit*, respectively. This was done so ***script.js*** can access the temperature number without the words "high" or "low" and also the temperature unit in order to convert them from Celsius to Fahrenheit and vice versa. All the information is presented as Jinja placeholders which ***app.py*** will then fill in with the forecast. Next, there is a Jinja loop that will iterate 4 times in order to render 4 other cards along with the current card, thus creating a 5-day forecast. Every card in this loop will contain the classes *five_day_forecast* and *ten_day_forecast* for the purpose of animation. The temperatures on these cards come from the *maxtemps* list that ***app.py*** gives this page. I index into the list in reverse because the info at the end of the list is the most current, and I start at index "-2" because the "-1" index is the current date's forecast, and that has already been presented on the current day card. Every card except the current day card also contains an ***li*** with a class of *date* that contains the date for that forecast. I get that information from the *sunrises* list, from index "-2" onwards like the temperatures, and more specifically from positions 5 through 10 at each index, because that will exclude the year and the time of the sunrise, so all we get is the date. Similarly, when I present the sunrise and sunset times, I get the information from the 11th position onwards at each index, thus excluding the date information and only getting the time. A final loop will take place after that, iterating 5 times and creating the remaining 5 days' cards, with all the same information as the previous 4, but including a class of *ten_cards* so they can be animated independently from the previous 5 cards. The forecast info on these cards is gathered from the lists from index "-6" onwards, to exclude the previous 5 cards.

```html

{% extends "layout.html" %}

{% block title %}
    Home
{% endblock %}

{% block main %}
    <div class="mx-auto mb-3">
        <p class="location">{{ location }}</p>
    </div>
    <div class="cards">
        <div class="card current_forecast pt-3 mb-3" id="today_card">
            <ul>
                <li class="current_temp"><span class="temp" celsius>{{ temp }}</span> <span class="temp_unit">°C</span></li>
                <div class="total_info_container">
                    <div class="info_container">
                        <div class="temp_container">
                            <li class="info maxtemp">High: <span class="temp" celsius>{{ maxtemp }}</span> <span class="temp_unit">°C</span></li>
                            <li class="info mintemp">Low: <span class="temp" celsius>{{ mintemp }}</span> <span class="temp_unit">°C</span></li>
                        </div>
                        <div class="sunrise_container">
                            <li class="info">Sunrise: {{ sunrise }}</li>
                            <li class="info">Sunset: {{ sunset }}</li>
                        </div>
                    </div>
                    <div class="additional_info_container">
                        <li class="info">Chance of Rain: {{ precipitation_chance }}%</li>
                        <li class="info">Windspeed: {{ windspeed }}km/h</li>
                    </div>
                </div>
            </ul>
        </div>
        {% for i in range(4) %}
            <div class="card five_day_forecast ten_day_forecast pt-3 mb-3" closed>
                <ul>
                    <li class="info maxtemps other_day_temp"><span class="temp" celsius>{{ maxtemps[-2 - i] }}</span> <span class="temp_unit">°C</span></li>
                    <li class="date">{{ sunrises[-2 - i][5:10] }}</li>
                    <div class="total_info_container">
                        <div class="info_container">
                            <div class="temp_container">
                                <li class="info mintemps">Low: <span class="temp" celsius>{{ mintemps[-2 - i] }}</span> <span class="temp_unit">°C</span></li>
                            </div>
                            <div class="sunrise_container">
                                <li class="info">Sunrise: {{ sunrises[-2 - i][11:] }}</li>
                                <li class="info">Sunset: {{ sunsets[-2 - i][11:] }}</li>
                            </div>
                        </div>
                        <div class="additional_info_container">
                            <li class="info">Chance of Rain: {{ precipitation_chances[-2 - i] }}%</li>
                        </div>
                    </div>
                </ul>
            </div>
        {% endfor %}
        {% for i in range(5) %}
            <div class="card ten_cards ten_day_forecast pt-3 mb-3" closed>
                <ul>
                    <li class="info maxtemps other_day_temp"><span class="temp" celsius>{{ maxtemps[-6 - i] }}</span> <span class="temp_unit">°C</span></li>
                    <li class="date">{{ sunrises[-6 - i][5:10] }}</li>
                    <div class="total_info_container">
                        <div class="info_container">
                            <div class="temp_container">
                                <li class="info mintemps">Low: <span class="temp" celsius>{{ mintemps[-6 - i] }}</span> <span class="temp_unit">°C</span></li>
                            </div>
                            <div class="sunrise_container">
                                <li class="info">Sunrise: {{ sunrises[-6 - i][11:] }}</li>
                                <li class="info">Sunset: {{ sunsets[-6 - i][11:] }}</li>
                            </div>
                        </div>
                        <div class="additional_info_container">
                            <li class="info">Chance of Rain: {{ precipitation_chances[-6 - i] }}%</li>
                        </div>
                    </div>
                </ul>
            </div>
        {% endfor %}
    </div>
{% endblock %}

```

<br>

The animations for this page are done by adding and subtracting ***HTML*** attributes to and from the cards onscreen. I had to animate them this way because simple transitions don't work when you want to set the cards' displays to "none". I didn't want to set their displays to "hidden" when they weren't needed because they would still take up space onscreen and push the current day forecast all the way to the left of the page. I wrote some ***CSS*** that performs the animations based on whether or not the cards have an attribute of *opening* or *closing*, and these attributes can only be set if the card currently has an attribute of *closed* or *open*, respectively. This means *opening* is only added when a card is *closed* and *closing* can only be added when a card is *open*. When opening, or displaying the cards, their display is changed to "flex", and their opacity is slowly increased while a translation occurs on either the X or Y-axis, depending on whether it's a 5 or 10-day forecast being displayed. The first 5 cards slide across the screen, while the remaining cards drop down from behind them. JavaScript will target the correct cards to animate based on the cards' classes and on whether the user clicked the "five-day" or "ten-day" forecast button. It will check for an *open* or *closed* attribute, add the corresponding *opening* or *closing* attribute, change the display to either"flex" or "none", wait for the animation to finish and then remove the *opening* or *closing* attribute and set the element's new current status to either *open* or *closed*. It will only do so once, whenever the button for the forecast is clicked, otherwise that event listener will remain active.

```css

.five_day_forecast[opening] {
    animation: slide-in 300ms forwards;
}

.five_day_forecast[closing] {
    animation: slide-out 750ms forwards;
}

.ten_cards[opening] {
    animation: slide-down 300ms forwards;
}

.ten_cards[closing] {
    animation: slide-up 300ms forwards;
}

.five_day_forecast,
.ten_day_forecast {
    display: none;
}

@keyframes slide-in {
    0% {
        transform: translateX(-600%);
    }

    100% {
        transform: translateX(0%);
    }
}

@keyframes slide-out {
    0% {
        transform: translateX(0%);
        opacity: 1;
    }

    50% {
        opacity: 0;
    }

    100% {
        transform: translateX(-600%);
    }
}

@keyframes slide-down {
    0% {
        transform: translateY(-100%);
        opacity: 0;
    }

    100% {
        transform: translateY(0%);
        opacity: 1;
    }
}

@keyframes slide-up {
    0% {
        transform: translateY(0%);
        opacity: 1;
    }

    50% {
        opacity: 0;
    }

    100% {
        transform: translateY(-100%);
        opacity: 0;
    }
}

```

<br>

```javascript

const today_button = document.getElementById('today');
const five_day_button = document.getElementById('five_day');
const ten_day_button = document.getElementById('ten_day');
let today_card = document.getElementById('today_card');
let five_cards = document.getElementsByClassName('five_day_forecast');
let ten_cards = document.getElementsByClassName('ten_cards');
let all_cards = document.getElementsByClassName('ten_day_forecast');

// Listen for 'today' button click
today_button.addEventListener('click', function() {
    for (let i = 0; i < all_cards.length; i++) {

        // assign and remove attributes to trigger CSS animations
        if (all_cards[i].hasAttribute('open') == true) {
            all_cards[i].removeAttribute('open');
            all_cards[i].setAttribute('closing', '');
            all_cards[i].setAttribute('closed', '');
            all_cards[i].addEventListener('animationend', function() {
                all_cards[i].style.display = 'none';
                all_cards[i].removeAttribute('closing');
            }, {

                // remove event listener once the animation ends
                once: true
            });
        }
    }
});

// Listen for 5-day forecast button click
five_day_button.addEventListener('click', function() {
    for (let i = 0; i < five_cards.length; i++) {

        // assign and remove attributes to trigger CSS animations
        if (five_cards[i].hasAttribute('closed') == true) {
            five_cards[i].removeAttribute('closed');
            five_cards[i].setAttribute('opening', '');
            five_cards[i].setAttribute('open', '');
            five_cards[i].style.display = 'flex';
            five_cards[i].addEventListener('animationend', function() {
                five_cards[i].removeAttribute('opening');
            }, {

                // remove event listener once the animation ends
                once: true
            });
        }
    }

    for (let i = 0; i < ten_cards.length; i++) {

        // assign and remove attributes to trigger CSS animations
        if (ten_cards[i].hasAttribute('open') == true) {
            ten_cards[i].removeAttribute('open');
            ten_cards[i].setAttribute('closing', '');
            ten_cards[i].setAttribute('closed', '');
            ten_cards[i].addEventListener('animationend', function() {
                ten_cards[i].removeAttribute('closing');
                ten_cards[i].style.display = 'none';
            }, {

                // remove event listener once the animation ends
                once: true
            });
        }
    }
});

// listen for 10-day forecast button click
ten_day_button.addEventListener('click', function() {
    for (let i = 0; i < all_cards.length; i++) {

        // assign and remove attributes to trigger CSS animations
        if (all_cards[i].hasAttribute('closed') == true) {
            all_cards[i].removeAttribute('closed');
            all_cards[i].setAttribute('opening', '');
            all_cards[i].setAttribute('open', '');
            all_cards[i].style.display = 'flex';
            all_cards[i].addEventListener('animationend', function() {
                all_cards[i].removeAttribute('opening');
            }, {

                // remove event listener once the animation ends
                once: true
            });
        }
    }
});

```

<br>

The user can also change the temperature units to either Celsius or Fahrenheit by clicking on the corresponding button, and this is also done in JavaScript. If the user clicks the Celcius button but the temperatures already have an attribute of *Celsius*, then nothing happens, and the same goes for Fahrenheit. If, however, the user clicks on a unit button and the temperatures can be converted, then either a function called ***convertToC()*** or ***convertToF()*** is called to perform the conversions. Then, the temperatures' *innerHTML* is changed to the converted temperature, and the unit's *innerHTML* is changed to the opposite unit. The unit attribute is added to the element, while the previous unit's attribute is removed, and this is done for every temperature onscreen.

```javascript

const celsius_button = document.getElementById('celsius');
const fahrenheit_button = document.getElementById('fahrenheit');
let temps = document.getElementsByClassName('temp');
let temp_units = document.getElementsByClassName('temp_unit');

function convertToF(value) {
    return Math.round(value * 9 / 5 + 32);
}

function convertToC(value) {
    return Math.round((value - 32) * 5 / 9);
}

// listen for celsius button click
celsius_button.addEventListener('click', function() {
    for (let i = 0; i < temps.length; i++) {

        // convert temperature and change temp unit if necessary
        if (temps[i].hasAttribute('fahrenheit') == true) {
            temps[i].innerHTML = convertToC(temps[i].innerHTML);
            temp_units[i].innerHTML = '°C';
            temps[i].removeAttribute('fahrenheit');
            temps[i].setAttribute('celsius', '');
        }
    }
});

// listen for fahrenheit button click
fahrenheit_button.addEventListener('click', function() {
    for (let i = 0; i < temps.length; i++) {

        // convert temperature and change temp unit if necessary
        if (temps[i].hasAttribute('celsius') == true) {
            temps[i].innerHTML = convertToF(temps[i].innerHTML);
            temp_units[i].innerHTML = '°F';
            temps[i].removeAttribute('celsius');
            temps[i].setAttribute('fahrenheit', '');
        }
    }
});

```

<br>

Finally, JavaScript will automatically check the *is_day* ***span*** on our page for either a 0 or a 1, and will change the background image and navbar color scheme accordingly. If the sun has not yet set, the navbar will remain a bright blue color `#279aed` and the background image will be of some pixelated clouds in the daytime. Otherwise, a darker purple color `#4e6cc2` is applied to the navbar and the background image will be of those same clouds in the nighttime.

```javascript

let is_day = document.getElementById('is_day');
let nav = document.getElementById('navbar');

if (is_day.hasAttribute('0') == true) {
    document.body.style.backgroundImage = "url('/static/background_night.jpg')";
    nav.style.backgroundColor = '#4e6cc2';
}

```

<br>

***changepass.html*** is the last page in this app and its layout is identical to ***register.html***. The differences are that the browser tab will read "Change Password", the page's title will read "Change Your Password" and the button to submit the form will read "Save Changes". Also, instead of having an input field for "username", there is a field for the old password.

```html

{% extends "layout.html" %}

{% block title %}
    Change Password
{% endblock %}

{% block main %}
    <div class="mx-auto mb-3">
        <p class="location">Change Your Password</p>
    </div>
    <form action="/changepass" method="post">
        <div class="mb-3">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto" name="password" placeholder="Current Password" type="password">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" name="new_password" placeholder="New Password" type="password">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" name="confirmation" placeholder="Confirm New Password" type="password">
        </div>
        <button class="btn btn-primary" type="submit">Save Changes</button>
    </form>
{% endblock %}

```

<br>

<h2 id="closer">Final Thoughts</h2>

Making this app taught me a lot about how the front and back-ends work together to take user input, exchange information with each other and then present new information back to the user. It taught me about styling and making the information you're presenting look nice so the user wants to return, and adding quality-of-life features to make the app feel more interactive and customizable. Writing JavaScript and CSS to interact with the HTML document to bring it to life and then seeing the code actually work brought me a sense of satisfaction that I'm sure I'll be chasing for as long as I continue to code. If nothing else, I'm thankful to CS50 for opening my eyes to this world of computer science where you can create, design, innovate, learn and explore new possibilities, awakening a sense of wonder and curiosity I thought only children had. I had a wonderful time taking this course and making this app. Thank you. THIS WAS CS50.

<br>

<div align="center">
    <a href="#title">Back to top</a>
</div># CS50-Final-Project
