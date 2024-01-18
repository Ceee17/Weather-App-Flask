# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User
from . import db, create_app
import requests

main = Blueprint('main', __name__)



@main.route('/')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('main.register'))

@main.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    #pake library yang sama buat check hashed password dari db
    if user and check_password_hash(user.password, password):
        # Successful login
        flash('Login successful!', 'success')
        # You might want to store the user's session here
        session['user_id'] = user.id

        return redirect(url_for('main.home'))
    else:
        # Failed login
        flash('Login failed. Please check your username and password.', 'danger')
        return redirect(url_for('main.login'))

@main.route('/login', methods=['GET'])    
def login():
    return render_template('login.html')

@main.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Logout Successfully!', 'success')
    return redirect(url_for('main.register'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Check if the username is unique
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('registration.html', error='Username already exists. Please choose a different one.')
        # disini default method buat hashnya itu 'pbkdf2:sha256' jadi kalo gamau diubah gaperlu tulis methodnya lagi
        hashed_password = generate_password_hash(password)
        # Create a new user
        new_user = User(username=username, password=hashed_password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('registration.html')

@main.route('/weather', methods=['GET', 'POST'])
def weather():
    api_key= 'b8434b7876803ad328b732a27ccea6d0'
    city = request.form.get('city') or 'Jakarta'

    #fetch data from OpenWeatherMap API
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')
   
    if response.status_code != 200:
        return "Error Fetching Current Weather Data"
    
    data = response.json()

    #fetch 3 day forecast data
    forecast_resp = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric')
    #error handling for fetching data
    if forecast_resp.status_code != 200:
        return "Error Fetching Forecast Data"
    forecast_data = forecast_resp.json()

    #prep and process data
    weather_data = {
        'city': data['name'],
        'temperature': data['main']['temp'],
        'conditions': data['weather'][0]['description'],
        'humidity': data['main']['humidity'],
        'wind_speed': data['wind']['speed'],
        'forecast': [
            {
                'date': forecast['dt_txt'],
                'conditions': forecast['weather'][0]['description'],
                'temperature': forecast['main']['temp'],
            }
            for forecast in forecast_data['list'][2:]
        ],
    }
    return render_template('weather.html', weather_data=weather_data)

@main.route('/quiz')    
def quiz():
    return render_template('quiz.html')
