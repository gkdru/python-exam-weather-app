from flask import Flask, request, render_template, make_response, redirect, url_for, g
from weather import get_weather
import sqlite3
import hashlib

app = Flask(__name__)


def hash_password(password):
    sha512 = hashlib.sha512() 
    sha512.update(password.encode("utf-8"))
    hashed_password = sha512.hexdigest()
    return hashed_password


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("users.db")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = hash_password(password)
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user_data = cursor.fetchone()

        if user_data:
            hashed_password_db = user_data[0]
            if hashed_password == hashed_password_db:
                response = make_response(redirect(url_for("weather")))
                response.set_cookie("username", username)
                response.set_cookie("password", hashed_password)
                return response
            else:
                return render_template(
                    "login.html", error="Invalid username or password"
                )
        else:
            return render_template("login.html", error="Invalid username or password")


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "GET":
        return render_template("signUp.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = hash_password(password)
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
        db.commit()
        response = make_response(redirect(url_for("weather")))
        response.set_cookie("username", username)
        response.set_cookie("password", hashed_password)
        return response


@app.route("/weather", methods=["GET", "POST"])
def weather():
    username = request.cookies.get("username")
    password = request.cookies.get("password")
    if username and password:
        welcome_message = f"Welcome, {username}! You are now logged in."
        city = request.args.get("city")
        if city:
            try:
                data = get_weather(city)
                if data:
                    img_src = (
                        "http://openweathermap.org/img/w/"
                        + data["weather"][0]["icon"]
                        + ".png"
                    )
                weather_text = f"""City: {data["name"]}.
                Main: {data["weather"][0]["main"]}.
                Temp_max: {data["main"]["temp_max"]}°C,
                Temp_min: {data["main"]["temp_min"]}°C.
                Wind speed: {data["wind"]["speed"]} m/s"""
                return render_template(
                    "weather.html",
                    data=weather_text.splitlines(),
                    img_src=img_src,
                    username=username,
                    welcome_message=welcome_message,
                )
            except KeyError:
                return render_template("error.html")
        else:
            return render_template("weather.html", welcome_message=welcome_message)
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
