from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import db, User
from openai import OpenAI
from PyPDF2 import PdfReader
from functools import wraps
import os
import json

routes = Blueprint("routes", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)
    return decorated_function

@routes.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

# Home route
@routes.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

# User registration
@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = generate_password_hash(data.get('password'))

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 400

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('routes.login'))
    return render_template('register.html')

# User login
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid username or password"}), 400

        session['user_id'] = user.id
        return redirect(url_for('routes.index'))

    return render_template('login.html')

# User logout
@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('routes.index'))

# Nebius API Config
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key='eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwNzE2MzI4NDkzNTM1MzY2Mzc1NiIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTg5NDMwNjM1MCwidXVpZCI6ImRiMzY2YWI3LTJjODEtNGVkZS1hYzZiLWY5Njg5MDgwYWQ1MyIsIm5hbWUiOiJIYWNrYXRob24iLCJleHBpcmVzX2F0IjoiMjAzMC0wMS0xMFQyMDoxMjozMCswMDAwIn0.Uqxspooor2Xnrzp6uoTnqvp3uwZW50M9uTklgkDPtoo'
)

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

@routes.route("/analyze_resume", methods=["POST"])
@login_required
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400
    
    resume_file = request.files["resume"]
    jobTitle = request.form.get("jobTitle", "")
    company = request.form.get("company", "")
    exprience = request.form.get("exprience", "")

    # Extract text from the PDF
    resume_text = extract_text_from_pdf(resume_file)

    # Nebius API Request
    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages=[
            {"role": "system", "content": "You are an AI career advisor specializing in resume analysis and job matching. Your task is to evaluate the provided resume and compare it with the target job role and company requirements. You must analyze the resume in depth and return the results in Markdown format."},  
            {"role": "user", "content": f'''### Resume Analysis Request  
            #### Resume Text:  
            {resume_text}  

            #### Target Job:  
            **Position:** {jobTitle}  
            **Company:** {company}  

            ### Evaluation Criteria:  
            1. **Career Readiness Score:** Provide a percentage (0-100%) indicating how well this resume matches the desired job role.  
            2. **Summary of the Candidate:** Write a concise summary of the candidate’s qualifications, experience, and strengths.
            3. **Where you can be Placed rn!:** According to summary where can they likely be placed with current qualifications, experience, and strengths.  
            4. **Weaknesses & Gaps:** Identify missing skills, gaps in experience, or relevant industry knowledge that the candidate lacks.  
            5. **Technologies to Learn:** List essential technologies, tools, or concepts the candidate should learn to increase job suitability.  
            6. **Project Suggestions:** Suggest projects the candidate can build to strengthen their portfolio and demonstrate the required skills.  

            ### Output Format:  
            Return your response in **Markdown format** with clear section headers, bullet points, and proper formatting for easy readability.'''}
        ],
        max_tokens=800,
        temperature=0.8,
        response_format={"type": "text"},
    )

    response_data = completion.to_json()
    return jsonify(json.loads(response_data))

@routes.route('/upload')
@login_required
def upload_resume():
    user = User.query.get(session['user_id'])
    return render_template("upload.html", user=user)


@routes.route('/chatbot')
@login_required
def chatbot():
    user = User.query.get(session['user_id'])
    # Fetch resume analysis data from session storage
    resume_analysis = session.get('resume_analysis')
    if not resume_analysis:
        return redirect(url_for('routes.upload_resume'))  # Redirect if no analysis data
    
    try:
        # Parse the analysis data
        analysis_data = json.loads(resume_analysis)
        analysis_text = analysis_data['choices'][0]['message']['content']
        
        # Debug: Print the analysis text
        print("Analysis Text:", analysis_text)
        
        return render_template("chatbot.html" , user=user)
    
    except (json.JSONDecodeError, KeyError) as e:
        # Handle parsing errors
        return redirect(url_for('routes.upload_resume'))

@routes.route('/chatbot', methods=['POST'])
@login_required
def chatbot_interaction():
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({"error": "Query is required"}), 400
    
    # Fetch resume analysis data from session storage
    resume_analysis = session.get('resume_analysis')
    if not resume_analysis:
        return jsonify({"error": "Resume analysis data not found"}), 400
    
    try:
        # Use Nebius API to generate a response
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are a career advisor. Provide guidance based on the user's resume analysis and query. return the results in Markdown format. chat with the user in a friendly and professional manner."},
                {"role": "user", "content": f"Resume Analysis: {resume_analysis}\n\nUser Query: {user_query}"}
            ],
            max_tokens=800,
            temperature=0.7,
            response_format={"type": "text"},
        )
        
        # Return the chatbot's response
        return jsonify({"message": completion.choices[0].message.content})
    
    except Exception as e:
        # Handle Nebius API errors
        return jsonify({"error": str(e)}), 500

@routes.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template("profile.html", user=user)

@routes.route('/coming_soon')
def coming_soon():
    return render_template("coming_soon.html")

@routes.route('/store_analysis', methods=['POST'])
@login_required
def store_analysis():
    data = request.json
    session['resume_analysis'] = json.dumps(data)
    return jsonify({"message": "Analysis data stored successfully"})