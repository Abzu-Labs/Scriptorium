# routes.py

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html') 

@app.route('/login')
def login():
    # Login logic
    return render_template('login.html')

@app.route('/signup')  
def signup():
    # Signup logic
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    # Get dashboard data
    return render_template('dashboard.html')

@app.route('/projects/<int:project_id>')
def project(project_id):
    # Get project data
    return render_template('project.html')

@app.route('/voice-cloning')
def voice_cloning():
    return render_template('voice_cloning.html')

@app.route('/voice-library')
def voice_library():
    # Get voice data
    return render_template('voice_library.html')  

@app.route('/settings')
def settings():
    return render_template('settings.html')