from flask import Flask, request, jsonify
from flask_caching import Cache
from user import User
import sqlite3
import requests

# Initialize Flask app
app = Flask(__name__)

# Configure Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 600})  # 10 minutes

# Your WeatherAPI.com API key
API_KEY = "c0df6556d94e4efb91394027241402"


# Initialize and set up SQLite database
def init_db():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, balance INTEGER)''')
        # Check if table is empty and if so, insert initial users
        c.execute('SELECT COUNT(*) FROM users')
        if c.fetchone()[0] == 0:
            users = [('User1', 5000), ('User2', 7500), ('User3', 10000), ('User4', 12500), ('User5', 15000)]
            c.executemany('INSERT INTO users (username, balance) VALUES (?, ?)', users)
        conn.commit()


init_db()


@app.route('/update_balance', methods=['POST'])
def update_balance():
    user_id = request.json.get('userId')
    city = request.json.get('city')
    user = User.get_user_by_id(user_id)
    if user:
        temp = fetch_weather_with_cache(city)
        if user.update_balance(temp):
            return jsonify({'message': 'Balance updated successfully'}), 200
        else:
            return jsonify({'message': 'Insufficient balance'}), 400
    else:
        return jsonify({'message': 'User not found'}), 404


@cache.memoize(timeout=600)
def fetch_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"
    response = requests.get(url)
    data = response.json()
    return data['current']['temp_c']


def fetch_weather_with_cache(city):
    return fetch_weather(city)


if __name__ == '__main__':
    app.run(debug=True)
