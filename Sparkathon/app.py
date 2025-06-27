from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

# Local modules for specific features
import chatbot
import visual_search
import quiz

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# ----------------- Database Setup -----------------
def init_users_table():
    # Ensures the user table exists in the DB
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT
        )
    ''')
    connection.commit()
    connection.close()

init_users_table()

def get_db_connection():
    return sqlite3.connect("users.db")


# ----------------- Routes -----------------

# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Chatbot Page
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot_page():
    if request.method == 'POST':
        user_input = request.form.get('query')
        if not user_input:
            flash("Please enter something before submitting.", "warning")
            return render_template('chatbot.html')

        reply = chatbot.get_response(user_input)
        return render_template('chatbot.html', response=reply, query=user_input)

    return render_template('chatbot.html')


# Visual Search Page
@app.route('/visual-search', methods=['GET', 'POST'])
def visualsearchpage():
    if request.method == 'POST':
        uploaded_image = request.files.get('product_image')

        if uploaded_image:
            matches = visual_search.search_by_image(uploaded_image)
            return render_template('visual_search.html', results=matches)
        else:
            flash("Please upload an image to search.", "error")

    return render_template('visualsearch.html')


# Quiz Page
@app.route('/quiz', methods=['GET', 'POST'])
def quiz_page():
    if request.method == 'POST':
        user_answers = {
            'budget': request.form.get('budget'),
            'style': request.form.get('style')
        }

        results = quiz.get_recommendations(user_answers)
        return render_template('quiz.html', recommendations=results)

    return render_template('quiz.html')


# ----------------- Auth Routes -----------------

# Sign Up Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            db = get_db_connection()
            db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (name, email, password))
            db.commit()
            flash("Account created! You can log in now.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already taken. Please choose another.", "error")
        finally:
            db.close()

    return render_template('signup.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (name, password)
        ).fetchone()
        conn.close()

        if user:
            session['user'] = name
            flash(f"Welcome, {name}!", "info")
            return redirect(url_for('home'))
        else:
            flash("Login failed. Please check your details.", "error")

    return render_template('login.html')


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You’ve been logged out.", "info")
    return redirect(url_for('home'))


# ----------------- Run App -----------------
if __name__ == '__main__':
    app.run(debug=True)  # Turn off debug for production
