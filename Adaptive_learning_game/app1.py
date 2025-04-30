from flask import Flask, request, jsonify, render_template
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import mysql.connector
import pickle
import pandas as pd
import os
import subprocess

app1 = Flask(__name__, template_folder='login/templates')
bcrypt = Bcrypt(app1)
CORS(app1)

# --- MySQL DB Connection Helper ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="adaptive"
    )

@app1.route('/profile/<username>')
def profile(username):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT MAX(score) FROM scores WHERE username = %s", (username,))
        result = cursor.fetchone()
        high_score = result[0] if result[0] is not None else "No scores yet"
        cursor.close()
        db.close()
        return render_template('profile.html', username=username, high_score=high_score)
    except Exception as e:
        return render_template('profile.html', username=username, high_score="Error loading score")

@app1.route('/signup', methods=['POST'])
def signup():
    data = request.json
    full_name = data.get('full_name')
    username = data.get('username')
    password = data.get('password')

    if not all([full_name, username, password]):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (full_name, username, password_hash) VALUES (%s, %s, %s)",
                       (full_name, username, hashed_password))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"message": "User registered successfully!"}), 200
    except mysql.connector.Error as err:
        print("Signup Error:", err)
        return jsonify({"error": "Username already exists or DB error"}), 400

@app1.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"error": "Missing username or password"}), 400

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and bcrypt.check_password_hash(user[0], password):
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app1.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.json
    username = data.get('username')
    subject = data.get('subject')
    quiz_topic = data.get('quiz_topic')
    score = data.get('score')
    total_questions = data.get('total_questions')

    if None in([username, subject, quiz_topic, score, total_questions]):
        return jsonify({"error": "Missing data"}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT score FROM scores WHERE username = %s AND subject = %s AND quiz_topic = %s
        """, (username, subject, quiz_topic))
        existing_score = cursor.fetchone()

        if existing_score:
            cursor.execute("""
                UPDATE scores SET score = %s, total_questions = %s, date = NOW()
                WHERE username = %s AND subject = %s AND quiz_topic = %s
            """, (score, total_questions, username, subject, quiz_topic))
        else:
            cursor.execute("""
                INSERT INTO scores (username, subject, quiz_topic, score, total_questions, date)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (username, subject, quiz_topic, score, total_questions))
        db.commit()
        cursor.close()
        db.close()

        # Optional: retrain model only if needed
        subprocess.call(['python', 'model/train_model.py'])

        return jsonify({"message": "Score processed and model retrained!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app1.route('/get_scores/<username>', methods=['GET'])
def get_scores(username):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT subject, score
            FROM scores WHERE username = %s
        """, (username,))
        scores_data = cursor.fetchall()
        cursor.close()
        db.close()

        if not scores_data:
            return jsonify({"error": "No scores found for the user"}), 404

        response_data = [
            {"subject": entry[0], "score": entry[1]}
            for entry in scores_data
        ]

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app1.route('/get_weak_subjects/<username>', methods=['GET'])
def get_weak_subjects(username):
    try:
        model_path = 'model/ml_model.pkl'
        feature_columns_path = 'model/feature_columns.pkl'

        if not os.path.exists(model_path) or not os.path.exists(feature_columns_path):
            return jsonify({"error": "Model or feature columns file not found"}), 500

        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(feature_columns_path, 'rb') as f:
            feature_columns = pickle.load(f)

        df = pd.read_csv("model/user_subjects.csv")
        user_df = df[df['username'] == username]

        if user_df.empty:
            return jsonify({"message": "No performance data available for user."}), 200

        X = user_df[feature_columns]
        preds = model.predict(X)

        weak_subjects = user_df[preds == 1]['subject'].tolist()
        return jsonify({"username": username, "weak_subjects": weak_subjects}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app1.run(debug=True)
