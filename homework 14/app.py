import requests
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# ================= USER CLASS =================
class User(UserMixin):
    def __init__(self, id, username, role='user'):
        self.id = id
        self.username = username
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('checkpoint2.db')
    user = conn.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return User(user[0], user[1], user[2]) if user else None

NEWS_API_KEY = '636f2f5d900f4de485ddb79db6a4465f'
WEATHER_API_KEY = '68f0bc3fbe4bde43c9acd9beb47b768e'


# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect('checkpoint2.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS city_cache (
            city TEXT PRIMARY KEY,
            cost_index REAL,
            updated_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS currency_rates (
            currency TEXT PRIMARY KEY,
            rate REAL,
            updated_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS travel_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city TEXT,
            days INTEGER,
            total_cost REAL,
            created_at TEXT
        )
    ''')

    conn.commit()
    conn.close()


# ================= WEATHER =================
def get_detailed_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        r = requests.get(url, timeout=5).json()

        if r.get("cod") == 200:
            return {
                "temp": int(r['main']['temp']),
                "humidity": r['main']['humidity'],
                "wind": r['wind']['speed'],
                "desc": r['weather'][0]['description'].capitalize(),
                "icon": r['weather'][0]['icon']
            }
    except:
        pass

    return None


# ================= HOME =================
@app.route('/')
def index():

    news = []

    try:
        url = f'https://newsapi.org/v2/everything?q=travel&language=en&pageSize=6&apiKey={NEWS_API_KEY}'
        news = requests.get(url).json().get('articles', [])
    except:
        pass

    return render_template('news.html', news=news)


# ================= QUIZ =================
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():

    questions = [
        {"id": 1, "text": "What is your ideal vacation vibe?",
         "options": [("A", "Luxury and shopping"), ("B", "Historic streets and cafes"), ("C", "Technology and nature")]},

        {"id": 2, "text": "Which climate do you prefer?",
         "options": [("A", "Hot and sunny"), ("B", "Mild European"), ("C", "Humid subtropical")]},

        {"id": 3, "text": "What is your priority?",
         "options": [("A", "Luxury service"), ("B", "Museums and culture"), ("C", "Food and gadgets")]},

        {"id": 4, "text": "How do you feel about crowds?",
         "options": [("A", "Love big cities"), ("B", "Prefer calm walks"), ("C", "Organized cities")]},

    ]

    recommendation = None
    weather = None

    if request.method == 'POST':

        answers = [request.form.get(f'q{i}') for i in range(1, 6)]

        if answers.count('A') >= 3:
            recommendation = "Dubai"

        elif answers.count('B') >= 3:
            recommendation = "London"

        else:
            recommendation = "Tokyo"

        weather = get_detailed_weather(recommendation)

    return render_template(
        'quiz.html',
        questions=questions,
        recommendation=recommendation,
        weather=weather
    )


# ================= CALCULATOR =================
@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():

    result = None
    weather = None

    if request.method == 'POST':

        city = request.form.get('city')
        days = int(request.form.get('days', 1))
        style = request.form.get('style')

        base_rate = 150 if style == 'luxury' else 70
        total = round(base_rate * days, 2)

        conn = sqlite3.connect('checkpoint2.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO travel_history (user_id, city, days, total_cost, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_user.id, city, days, total, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        result = {
            "city": city,
            "days": days,
            "total": total
        }

        weather = get_detailed_weather(city)

    return render_template('calculator.html', result=result, weather=weather)


# ================= HISTORY =================
@app.route('/history')
@login_required
def history():

    conn = sqlite3.connect('checkpoint.db')

    rows = conn.execute(
        'SELECT * FROM travel_history WHERE user_id = ? ORDER BY id DESC',
        (current_user.id,)
    ).fetchall()

    conn.close()

    return render_template('history.html', rows=rows)


# ================= AUTH =================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:

            conn = sqlite3.connect('checkpoint2.db')

            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, 'user')
            )

            conn.commit()
            conn.close()

            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash("User already exists")

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('checkpoint2.db')

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            user_obj = User(user[0], user[1], user[3])

            login_user(user_obj)

            return redirect(url_for('index'))

        flash("Wrong login or password")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('index'))


# ================= ADMIN =================
def admin_required(f):

    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):

        if current_user.role != 'admin':

            flash("Admins only")

            return redirect(url_for('index'))

        return f(*args, **kwargs)

    return decorated


@app.route('/admin')
@admin_required
def admin():

    conn = sqlite3.connect('checkpoint2.db')

    users = conn.execute(
        "SELECT id, username, role FROM users"
    ).fetchall()

    conn.close()

    return f"Users: {users}"


# ================= RUN =================
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5002)