Got it! The formatting error in your `README.md` is caused by incorrect usage of triple backticks and markdown syntax.

---

### ✅ Fixed and Beautified `README.md`

Here’s a clean version with all formatting corrected — **copy and paste this** into your `README.md` file:

````md
# AI Resume Matcher 🚀

An AI-powered resume scoring app built with **FastAPI** and **XGBoost**. Upload a PDF resume and get a match score based on your company's job description.

---

## 📦 Getting Started

### 1. Clone this repository

```bash
git clone https://github.com/Katechnology/ai_resume_app.git
cd ai_resume_app
```
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app locally

```bash
uvicorn main:app --reload
```

Visit: [http://localhost:8000](http://localhost:8000)

---

## 🗂 Folder Structure

```
ai_resume_app/
├── main.py               # FastAPI backend
├── templates/            # HTML frontend
├── static/               # Background image, CSS
├── saved_model/          # Model and vectorizers (.pkl files)
├── requirements.txt
└── README.md
```

---

## 🤖 Model Details

- Trained on cleaned resume data
- Features used:
  - TF-IDF of role, skills, summary
  - Scaled experience years
- Model: `XGBRegressor`

---

## 🛡 License

This project is licensed under the MIT License.  
Feel free to fork and build upon it!

---

## ✨ Credits

Made with ❤️ by [@Katechnology](https://github.com/Katechnology)

```

---

```
