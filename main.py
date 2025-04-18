from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import shutil
import os
import fitz  # PyMuPDF
import joblib
import re
import numpy as np
from scipy.sparse import hstack
from fastapi.staticfiles import StaticFiles



app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"
MODEL_FOLDER = "saved_model"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def semicolon_tokenizer(text):
    return text.split(';')

# Load models
model = joblib.load(os.path.join(MODEL_FOLDER, "xgb_model.pkl"))
tfidf_role = joblib.load(os.path.join(MODEL_FOLDER, "tfidf_role.pkl"))
tfidf_skills = joblib.load(os.path.join(MODEL_FOLDER, "tfidf_skills.pkl"))
tfidf_summary = joblib.load(os.path.join(MODEL_FOLDER, "tfidf_summary.pkl"))
scaler = joblib.load(os.path.join(MODEL_FOLDER, "experience_scaler.pkl"))

# ========== Resume Parsing Functions ==========
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group() if match else ""

def extract_phone(text):
    match = re.search(r'\+?\d[\d\s\-]{8,15}', text)
    return match.group() if match else ""

def extract_links(text):
    links = []

    # Match LinkedIn
    linkedin_match = re.search(r'(linkedin\.com/in/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if linkedin_match:
        links.append("https://" + linkedin_match.group(1))

    # Match GitHub
    github_match = re.search(r'(github\.com/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    if github_match:
        links.append("https://" + github_match.group(1))

    return links

def extract_name(text):
    lines = text.strip().split('\n')[:10]
    for line in lines:
        clean = line.strip()
        # Ignore if line contains contact info or known words
        if "@" in clean or any(x in clean.lower() for x in ["linkedin", "github", "email", "phone", "curriculum", "vitae"]):
            continue
        words = clean.split()
        if 1 < len(words) <= 4 and all(w[0].isupper() for w in words if w):
            return clean
    return ""


def extract_skills(text):
    skill_keywords = [
    "Python", "SQL", "Tableau", "Power BI", "R", "Pandas", "NumPy", "Scikit-learn",
    "MySQL", "PostgreSQL", "Excel", "Java", "C++", "Machine Learning", "Deep Learning",
    "Statistics", "Data Visualization", "Data Mining", "Big Data", "Hadoop", "Spark",
    "Airflow", "Git", "Docker", "Kubernetes", "Data Wrangling", "Data Cleaning",
    "Natural Language Processing", "Computer Vision", "Seaborn", "Matplotlib", "Plotly",
    "ETL Pipelines", "AWS", "Azure", "Google Cloud Platform (GCP)", "Feature Engineering",
    "Model Evaluation", "Model Deployment", "MLOps", "Data Lakes", "Snowflake",
    "Data Governance", "A/B Testing", "Data Ethics", "Bayesian Inference", "EDA",
    "Transformers", "Hugging Face", "FastAPI", "Dask"
    ]
    skill_keywords = [skill.lower() for skill in skill_keywords]
    text = text.lower()
    return [skill for skill in skill_keywords if skill in text]

import re

def extract_degrees(raw_text):
    """
    Extracts academic degree information from raw CV/resume text.

    Args:
        raw_text (str): The raw text from a CV or resume.

    Returns:
        List[str]: A list of extracted degree strings.
    """
    degree_pattern = re.compile(
        r'\b(Bachelor|Master|Doctor|Associate)[\w\s]* in [^\n]+',
        re.IGNORECASE
    )
    match = degree_pattern.search(raw_text)
    return match.group().strip() if match else ''

def extract_experience_years(text):
    match = re.findall(r'(\d+)\+?\s*years?', text.lower())
    return max([int(m) for m in match], default=0)

def extract_role(text):
    role_keywords = [
    "Data Analyst", "Data Scientist", "Business Analyst", "Machine Learning Engineer",
    "AI Engineer", "BI Developer", "Quantitative Analyst", "Data Engineer",
    "Big Data Engineer", "Research Scientist", "Analytics Consultant",
    "Decision Scientist", "Data Architect", "Data Strategist", "Statistical Programmer",
    "ML Ops Engineer", "NLP Engineer", "Computer Vision Engineer", "Product Data Analyst",
    "Data Journalist", "Business Intelligence Analyst", "Healthcare Data Analyst",
    "Customer Insights Analyst", "Operations Analyst", "Marketing Data Analyst",
    "Financial Data Analyst", "Growth Analyst", "Risk Analyst", "Fraud Analyst",
    "Research Analyst", "CRM Analyst", "Data Quality Analyst", "IoT Data Analyst",
    "Sports Data Scientist", "Retail Data Analyst", "Actuarial Data Scientist",
    "Data Science Manager", "AI Product Manager", "Data Analytics Lead",
    "Public Policy Data Analyst", "Transportation Data Analyst", "HR Data Analyst",
    "Climate Data Scientist", "Geospatial Data Analyst", "Open Source Contributor (Data)",
    "Data Science Instructor", "AI Ethicist", "Knowledge Graph Engineer",
    "Data Consultant", "Personalized Systems Specialist"
    ]
    text_lower = text.lower()
    role_keywords = [role.lower() for role in role_keywords]

    for role in role_keywords:
        if role in text_lower:
            return role.title()

    return "Unknown"
def extract_summary(text):
    # Use case-insensitive regex to find 'Summary' and 'Skills'
    pattern = re.compile(r'Summary(.*?)Core Skills', re.DOTALL | re.IGNORECASE)
    match = pattern.search(text)
    if match:
        summary = match.group(1).strip()
        return summary
    return ""
def parse_resume(file_path):
    text = extract_text_from_pdf(file_path)


    return {
        "summary": extract_summary(text),
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "links": "; ".join(extract_links(text)),
        "role": extract_role(text),
        "skills": "; ".join(extract_skills(text)),
        "education": extract_degrees(text),
        "experience_years": extract_experience_years(text)
    }

# ========== Web Interface ==========
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.api_route("/upload", methods=["GET", "POST"])
async def upload_resume(request: Request, file: UploadFile = File(None)):
    if request.method == "GET":
        # User visited /upload or refreshed it — just show form
        return templates.TemplateResponse("index.html", {"request": request})

    # Safe POST logic
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed = parse_resume(file_path)

    # Vectorize and predict
    X_role = tfidf_role.transform([parsed["role"]])
    X_skills = tfidf_skills.transform([parsed["skills"]])
    X_summary = tfidf_summary.transform([parsed["summary"]])
    X_experience = scaler.transform([[parsed["experience_years"]]])

    X_final = hstack([X_role, X_skills, X_summary, X_experience])
    score = model.predict(X_final)[0]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "score": round(score, 2),
        "name": parsed["name"],
        "phone": parsed["phone"],
        "links": parsed["links"],
    })

# To run locally: uvicorn app:app --reload
