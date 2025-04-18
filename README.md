# AI Resume Matcher 🚀

An AI-powered resume scoring app built with **FastAPI** and **XGBoost**. Upload a PDF resume and get a match score based on your company's job description.

![screenshot](https://github.com/Katechnology/ai_resume_app/blob/main/static/background.jpg?raw=true)

---

## 🔍 Features

- 📄 Upload PDF resumes
- 🧠 Extracts name, phone, LinkedIn, GitHub
- 🔢 Calculates match score using a trained ML model
- 🎨 Clean UI with file upload preview and progress bar
- 💻 Built with FastAPI, Python, Scikit-learn, XGBoost

---

## 🚀 Getting Started

### 1. Clone this repository

````bash
git clone https://github.com/Katechnology/ai_resume_app.git
cd ai_resume_app

### 2. Install dependencies
```bash
pip install -r requirements.txt

### 3. Run the app locally
```bash
uvicorn main:app --reload

Visit: http://localhost:8000

📁 Folder Structure
ai_resume_app/
├── main.py               # FastAPI backend
├── templates/            # HTML frontend
├── static/               # Background image, CSS
├── saved_model/          # Model and vectorizers (.pkl files)
├── requirements.txt
└── README.md

🤖 Model Details
Trained on cleaned resume data
Model: XGBRegressor

🛡 License
This project is licensed under the MIT License.
Feel free to fork and build upon it!

✨ Credits
Made with ❤️ by @Katechnology
````
