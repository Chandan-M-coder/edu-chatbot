from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Database setup
def init_db():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    
    # Create questions table
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY, 
                  question TEXT, 
                  answer TEXT,
                  category TEXT)''')
    
    # Insert some sample educational data
    sample_data = [
        ("What is Python?", "Python is a programming language used for web development, data science, and more.", "programming"),
        ("What is 2+2?", "2 + 2 = 4", "math"),
        ("What is photosynthesis?", "Photosynthesis is how plants make food using sunlight.", "science"),
        ("How to study effectively?", "Take breaks, practice regularly, and get enough sleep.", "study tips")
    ]
    
    c.executemany("INSERT OR IGNORE INTO questions (question, answer, category) VALUES (?, ?, ?)", sample_data)
    conn.commit()
    conn.close()

# Initialize database when server starts
init_db()

def find_answer(user_question):
    """Simple function to find answer in database"""
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    
    # Convert user question to lowercase for better matching
    user_question = user_question.lower()
    
    # Search for matching questions
    c.execute("SELECT question, answer FROM questions")
    all_questions = c.fetchall()
    
    best_match = None
    best_answer = "I'm still learning. Can you ask about math, science, or programming?"
    
    for db_question, db_answer in all_questions:
        db_question_lower = db_question.lower()
        
        # Simple keyword matching
        if any(word in user_question for word in db_question_lower.split()):
            best_answer = db_answer
            best_match = db_question
            break
    
    conn.close()
    return best_answer

@app.route('/')
def home():
    return "Chatbot Server is Running!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get user message from frontend
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get bot response
        bot_response = find_answer(user_message)
        
        # Save chat to database (optional)
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute("INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)", 
                 (user_message, bot_response))
        conn.commit()
        conn.close()
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add-question', methods=['POST'])
def add_question():
    """Add new question-answer pair to database"""
    try:
        data = request.json
        question = data.get('question')
        answer = data.get('answer')
        category = data.get('category', 'general')
        
        conn = sqlite3.connect('chatbot.db')
        c = conn.cursor()
        c.execute("INSERT INTO questions (question, answer, category) VALUES (?, ?, ?)", 
                 (question, answer, category))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Question added successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create chat history table
def setup_chat_history():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY,
                  user_message TEXT,
                  bot_response TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Run this when server starts
setup_chat_history()

if __name__ == '__main__':
    print("🚀 Starting Educational Chatbot Server...")
    print("📚 Database initialized with sample questions")
    print("🌐 Server running at: http://localhost:5000")
    app.run(debug=True, port=5000)