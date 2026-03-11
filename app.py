import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Goal, Expense
import json
import google.generativeai as genai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'finlearn.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Configure Google Generative AI
genai.configure(api_key="AIzaSyD2MiBty310A0gc1RTG3w5ou1z2kXez1tk")
model = genai.GenerativeModel("gemini-1.5-flash")

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def update_streak(user):
    today = date.today().isoformat()
    last_login = user.last_login

    if last_login == today:
        return # Already logged in today

    if last_login:
        last_date = date.fromisoformat(last_login)
        if last_date == date.today() - timedelta(days=1):
            user.streak += 1
        else:
            user.streak = 1
    else:
        user.streak = 1
        
    user.last_login = today
    db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data["message"]

    prompt = f"""
    You are an AI finance assistant for a platform called FinLearn.
    Help young users understand financial concepts like:

    - budgeting
    - saving
    - investing
    - SIP
    - mutual funds
    - credit score

    Explain everything in simple language.

    User Question:
    {user_message}
    """

    response = model.generate_content(prompt)

    return jsonify({"reply": response.text})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('fullname')
        username = request.form.get('username')
        dob = request.form.get('dob')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('signup'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.', 'error')
            return redirect(url_for('signup'))
            
        user_by_uname = User.query.filter_by(username=username).first()
        if user_by_uname:
            flash('Username already exists.', 'error')
            return redirect(url_for('signup'))

        new_user = User(
            full_name=full_name,
            username=username,
            dob=dob,
            email=email,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256')
        )

        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        update_streak(new_user)
        return redirect(url_for('profile'))

    return render_template('auth/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('login'))

        login_user(user)
        update_streak(user)
        return redirect(url_for('profile'))

    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/learning-hub')
def learning_hub():
    return render_template('learning.html')

@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')

@app.route('/spending-tracker')
@login_required
def spending_tracker():
    return render_template('tracker.html')

@app.route('/leaderboard')
def leaderboard():
    top_users = User.query.order_by(User.points.desc()).limit(10).all()
    return render_template('leaderboard.html', top_users=top_users)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        goal_name = request.form.get('goal_name')
        amount_required = request.form.get('amount_required')
        if goal_name and amount_required:
            new_goal = Goal(user_id=current_user.id, name=goal_name, amount_required=float(amount_required))
            db.session.add(new_goal)
            db.session.commit()
            flash('Goal added successfully!', 'success')
            return redirect(url_for('profile'))
            
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, goals=goals)

# --- QUIZ API (20 Levels x 10 Questions) ---
@app.route('/api/get_level_data/<int:level>')
@login_required
def get_level_data(level):
    if level < 1 or level > 20:
        return jsonify({'error': 'Invalid level'}), 400
        
    try:
        with open(os.path.join(basedir, 'questions.json'), 'r') as f:
            all_questions = json.load(f)
        questions = [q for q in all_questions if q['level'] == level]
        # Remove 'answer' and 'explanation' to prevent cheating from client side
        for q in questions:
            q.pop('answer', None)
            q.pop('explanation', None)
    except Exception as e:
        questions = []
        
    return jsonify({'level': level, 'questions': questions})

@app.route('/api/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    data = request.json
    selected_option = data.get('selected_option')
    question_id = data.get('question_id')
    
    try:
        with open(os.path.join(basedir, 'questions.json'), 'r') as f:
            all_questions = json.load(f)
        question = next((q for q in all_questions if q['id'] == question_id), None)
    except:
        question = None

    if not question:
        return jsonify({'error': 'Question not found'}), 404

    is_correct = (selected_option == question['answer'])
    points_earned = 0
    new_badges = []
    
    if is_correct:
        points_earned = 10
        current_user.points += points_earned
        
        # Check for certificate unlocks
        certs = current_user.get_certificates()
        thresholds = {1000: 'Growing Up', 5000: 'Proficient', 10000: 'Master'}
        
        for req_points, badge_name in thresholds.items():
            if current_user.points >= req_points and badge_name not in certs:
                current_user.add_certificate(badge_name)
                new_badges.append(badge_name)
                
        db.session.commit()
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': question['answer'],
        'explanation': question['explanation'],
        'points_earned': points_earned,
        'new_total_points': current_user.points,
        'new_badges_unlocked': new_badges
    })

# Initialize DB on first run
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
