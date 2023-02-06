from flask import Flask, render_template, request, redirect, url_for
import requests
import datetime
import time

app = Flask(__name__)


# Argument is passed in from an HTML form in base.html
# JSON contains coordinates and other location data
def get_coordinates(location):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=5&appid=6cfc80704392243545d62c289f23e5ad"
    req = requests.get(url).json()
    return req


# JSON contains various weather, time, and location data
# Calling this API using coordinates provides more precision and is more reliable than calling by city names, according to documentation
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=6cfc80704392243545d62c289f23e5ad&units=metric"
    req = requests.get(url).json()
    return req


# Converts UNIX time to UTC
# Depending on time of day, switch backgrounds
def change_background(timezone):
    t = int(datetime.datetime.utcfromtimestamp(timezone + time.time()).strftime('%H'))

    if t in range(5, 15):
        return "day"
    elif t in range(15, 20):
        return "afternoon"
    elif t in range(0, 5) or t in range(20, 24):
        return "night"


@app.route("/", methods=["GET"])
def base():
    return render_template("base.html")


@app.route("/index", methods=["GET", "POST"])
def weather_post():
    if request.method == "POST":
        location = request.form.get("location")
        req = get_coordinates(location)

        # If the location can not be found, redirect to base.html
        if req:
            weather_data = get_weather(req[0]["lat"], req[0]["lon"])
            data = {
                "city": req[0]["name"],
                "state": "",
                "country": req[0]["country"],
                "temp": weather_data["main"]["temp"],
                "low": weather_data["main"]["temp_min"],
                "high": weather_data["main"]["temp_max"],
                "wind": weather_data["wind"]["speed"],
                "humidity": weather_data["main"]["humidity"],
                "sunrise": datetime.datetime.fromtimestamp(weather_data["sys"]["sunrise"]).strftime('%H:%M'),
                "sunset": datetime.datetime.fromtimestamp(weather_data["sys"]["sunset"]).strftime('%H:%M'),
                "description": weather_data["weather"][0]["description"],
                "icon": weather_data["weather"][0]["icon"],
                "time_hour": datetime.datetime.utcfromtimestamp(weather_data["timezone"] + weather_data["dt"]).strftime('%H'),
                "time_minute": datetime.datetime.utcfromtimestamp(weather_data["dt"]).strftime(':%M'),
                "image": change_background(weather_data["timezone"])
            }
            # Append state code if it exists (US only)
            if data["country"] == "US":
                data["state"] = req[0]["state"] + ", "

            return render_template("index.html", data=data)
        else:
            return redirect(url_for("base"))
    else:
        # If "GET"
        return redirect(url_for("base"))


if __name__ == "__main__":
    app.run(debug=True)
