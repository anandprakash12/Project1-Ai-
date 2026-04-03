# # =========================================================
# # AI Resume Ranking System (FINAL INDUSTRY VERSION)
# # =========================================================
# import streamlit as st
# import PyPDF2
# import re
# import torch
# import pandas as pd
# import matplotlib.pyplot as plt
# from transformers import BertTokenizer, BertModel
# from sklearn.metrics.pairwise import cosine_similarity
# import mysql.connector

# # -------------------------------
# # PAGE CONFIG
# # -------------------------------
# st.set_page_config(page_title="AI Resume Ranking System", layout="wide")

# # -------------------------------
# # DATABASE CONNECTION (MOVE HERE)
# # -------------------------------
# try:
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="your_password",  # CHANGE THIS
#         database="resume_ai"
#     )
#     cursor = conn.cursor()
# except:
#     conn = None
#     cursor = None

# # -------------------------------
# # LOGIN / SIGNUP SYSTEM
# # -------------------------------
# if "login" not in st.session_state:
#     st.session_state["login"] = False

# menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

# def signup():
#     st.title("📝 Create Account")

#     new_user = st.text_input("Username")
#     new_pass = st.text_input("Password", type="password")

#     if st.button("Signup"):
#         if conn is None:
#             st.error("Database not connected")
#             return

#         cursor.execute("SELECT * FROM users WHERE username=%s", (new_user,))
#         if cursor.fetchone():
#             st.warning("User already exists")
#         else:
#             cursor.execute(
#                 "INSERT INTO users (username, password) VALUES (%s,%s)",
#                 (new_user, new_pass)
#             )
#             conn.commit()
#             st.success("Account created! Go to Login")

# def login():
#     st.title("🔐 Login")

#     user = st.text_input("Username")
#     pwd = st.text_input("Password", type="password")

#     if st.button("Login"):
#         if conn is None:
#             st.error("Database not connected")
#             return

#         cursor.execute(
#             "SELECT * FROM users WHERE username=%s AND password=%s",
#             (user, pwd)
#         )
#         data = cursor.fetchone()

#         if data:
#             st.session_state["login"] = True
#             st.success("Login Successful")
#         else:
#             st.error("Invalid Credentials")

# # SHOW MENU
# if menu == "Signup":
#     signup()

# elif menu == "Login":
#     login()

# # STOP if not logged in
# if not st.session_state["login"]:
#     st.stop()

# # # -------------------------------
# # # DATABASE CONNECTION
# # # -------------------------------
# # try:
# #     conn = mysql.connector.connect(
# #         host="localhost",
# #         user="root",
# #         password="your_password",  # CHANGE THIS
# #         database="resume_ai"
# #     )
# #     cursor = conn.cursor()
# # except:
# #     conn = None

# # -------------------------------
# # LOAD BERT MODEL
# # -------------------------------
# @st.cache_resource
# def load_model():
#     tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
#     model = BertModel.from_pretrained('bert-base-uncased')
#     return tokenizer, model

# tokenizer, model = load_model()

# # -------------------------------
# # FUNCTIONS
# # -------------------------------
# def extract_text(file):
#     reader = PyPDF2.PdfReader(file)
#     text = ""
#     for page in reader.pages:
#         if page.extract_text():
#             text += page.extract_text()
#     return text

# def preprocess(text):
#     return re.sub(r'\W+', ' ', text.lower())

# def get_embedding(text):
#     inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     return outputs.last_hidden_state.mean(dim=1)

# def similarity(a, b):
#     return cosine_similarity(a.numpy(), b.numpy())[0][0]

# skills_db = ["python","sql","excel","machine learning","deep learning","tableau","power bi","nlp"]

# def extract_skills(text):
#     return [s for s in skills_db if s in text]

# def extract_experience(text):
#     match = re.findall(r'(\d+)\s+years', text)
#     return match[0]+" yrs" if match else "Fresher"

# def save_to_db(data):
#     if conn:
#         for r in data:
#             cursor.execute("""
#             INSERT INTO results (name, score, skills, experience)
#             VALUES (%s,%s,%s,%s)
#             """,(r['name'], r['score'], ",".join(r['skills']), r['experience']))
#         conn.commit()

# # -------------------------------
# # HEADER
# # -------------------------------
# st.title("🧠 AI Resume Ranking Dashboard")

# job_desc = st.text_area("📌 Job Description")
# files = st.file_uploader("📂 Upload Resumes", accept_multiple_files=True)

# # -------------------------------
# # PROCESS
# # -------------------------------
# if st.button("🚀 Analyze"):

#     if not job_desc or not files:
#         st.warning("Enter job description & upload resumes")
#     else:
#         resumes_data = []

#         jd_emb = get_embedding(preprocess(job_desc))

#         for f in files:
#             text = extract_text(f)
#             clean = preprocess(text)
#             emb = get_embedding(clean)
#             score = similarity(emb, jd_emb)

#             resumes_data.append({
#                 "name": f.name,
#                 "score": score,
#                 "skills": extract_skills(clean),
#                 "experience": extract_experience(clean)
#             })

#         resumes_data = sorted(resumes_data, key=lambda x: x["score"], reverse=True)

#         # -------------------------------
#         # METRICS
#         # -------------------------------
#         c1, c2, c3 = st.columns(3)
#         c1.metric("Total Resumes", len(resumes_data))
#         c2.metric("Processed", len(resumes_data))
#         c3.metric("Success Rate", "100%")

#         st.divider()

#         # -------------------------------
#         # SEARCH + FILTER
#         # -------------------------------
#         search = st.text_input("🔍 Search")
#         min_score = st.slider("Minimum Score", 0.0, 1.0, 0.0)

#         filtered = [
#             r for r in resumes_data
#             if search.lower() in str(r).lower() and r['score'] >= min_score
#         ]

#         # -------------------------------
#         # DISPLAY CARDS
#         # -------------------------------
#         for r in filtered:
#             st.markdown(f"""
#             <div style="
#                 background: linear-gradient(135deg, #4CAF50, #2E7D32);
#                 padding: 20px;
#                 border-radius: 15px;
#                 color: white;
#                 margin-bottom: 10px;">
                
#                 <h3>👤 {r['name']}</h3>
#                 <p>🎯 Score: {r['score']:.2f}</p>
#                 <p>📅 Experience: {r['experience']}</p>
#                 <p>🧠 Skills: {', '.join(r['skills'])}</p>
#             </div>
#             """, unsafe_allow_html=True)

#         # -------------------------------
#         # CHART
#         # -------------------------------
#         names = [r['name'] for r in filtered]
#         scores = [r['score'] for r in filtered]

#         fig, ax = plt.subplots()
#         ax.barh(names, scores)
#         st.pyplot(fig)

#         # -------------------------------
#         # SAVE TO DB
#         # -------------------------------
#         save_to_db(filtered)

#         # -------------------------------
#         # EXPORT
#         # -------------------------------
#         df = pd.DataFrame(filtered)
#         st.download_button("📤 Export CSV", df.to_csv(index=False), "results.csv")





# =========================================================
# AI Resume Ranking System (ULTRA PREMIUM FINAL VERSION)
# =========================================================

import streamlit as st
import PyPDF2
import re
import torch
import pandas as pd
import plotly.express as px
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import mysql.connector

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Resume Ranking System", layout="wide")

# -------------------------------
# DATABASE CONNECTION (FIXED)
# -------------------------------
try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",   # ✅ EMPTY (IMPORTANT)
        database="resume_ai",
        port=3306
    )
    cursor = conn.cursor()
    st.success("✅ Database Connected")

except Exception as e:
    conn = None
    cursor = None
    st.error(f"❌ Database Error: {e}")

# -------------------------------
# SESSION STATE
# -------------------------------
if "login" not in st.session_state:
    st.session_state["login"] = False

# -------------------------------
# SIGNUP FUNCTION
# -------------------------------
def signup():
    st.title("📝 Create Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Signup"):
        if conn is None:
            st.error("Database not connected")
            return

        cursor.execute("SELECT * FROM users WHERE username=%s", (new_user,))
        if cursor.fetchone():
            st.warning("User already exists")
        else:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s,%s)",
                (new_user, new_pass)
            )
            conn.commit()
            st.success("Account created! Go to Login")

# -------------------------------
# LOGIN FUNCTION
# -------------------------------
def login():
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if conn is None:
            st.error("Database not connected")
            return

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (user, pwd)
        )
        data = cursor.fetchone()

        if data:
            st.session_state["login"] = True
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

# -------------------------------
# MENU
# -------------------------------
menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

if menu == "Signup":
    signup()
elif menu == "Login":
    login()

if not st.session_state["login"]:
    st.stop()

# -------------------------------
# LOAD BERT MODEL
# -------------------------------
@st.cache_resource
def load_model():
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    return tokenizer, model

tokenizer, model = load_model()

# -------------------------------
# FUNCTIONS
# -------------------------------
def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def preprocess(text):
    return re.sub(r'\W+', ' ', text.lower())

def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

def similarity(a, b):
    return cosine_similarity(a.numpy(), b.numpy())[0][0]

skills_db = ["python","sql","excel","machine learning","deep learning","tableau","power bi","nlp"]

def extract_skills(text):
    return [s for s in skills_db if s in text]

def extract_experience(text):
    match = re.findall(r'(\d+)\s+years', text)
    return match[0]+" yrs" if match else "Fresher"

def save_to_db(data):
    if conn:
        for r in data:
            cursor.execute("""
            INSERT INTO results (name, score, skills, experience)
            VALUES (%s,%s,%s,%s)
            """,(r['name'], r['score'], ",".join(r['skills']), r['experience']))
        conn.commit()

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<h1 style='text-align:center;'>🧠 AI Resume Ranking Dashboard</h1>
<p style='text-align:center; color:gray;'>Ultra Premium AI System</p>
""", unsafe_allow_html=True)

# -------------------------------
# INPUT
# -------------------------------
col1, col2 = st.columns([2,1])

with col1:
    job_desc = st.text_area("📌 Job Description")

with col2:
    files = st.file_uploader("📂 Upload Resumes", accept_multiple_files=True)

# -------------------------------
# PROCESS
# -------------------------------
if st.button("🚀 Analyze Resumes"):

    if not job_desc or not files:
        st.warning("Enter job description & upload resumes")
    else:
        resumes_data = []
        jd_emb = get_embedding(preprocess(job_desc))

        for f in files:
            text = extract_text(f)
            clean = preprocess(text)
            emb = get_embedding(clean)
            score = similarity(emb, jd_emb)

            resumes_data.append({
                "name": f.name,
                "score": score,
                "skills": extract_skills(clean),
                "experience": extract_experience(clean)
            })

        resumes_data = sorted(resumes_data, key=lambda x: x["score"], reverse=True)

        # -------------------------------
        # METRICS
        # -------------------------------
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Resumes", len(resumes_data))
        c2.metric("Top Score", f"{resumes_data[0]['score']:.2f}")
        c3.metric("Success Rate", "100%")

        st.divider()

        # -------------------------------
        # FILTER
        # -------------------------------
        search = st.text_input("🔍 Search")
        min_score = st.slider("Score Filter", 0.0, 1.0, 0.0)

        filtered = [
            r for r in resumes_data
            if search.lower() in str(r).lower() and r['score'] >= min_score
        ]

        # -------------------------------
        # DISPLAY
        # -------------------------------
        for r in filtered:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #4CAF50, #2E7D32);
                padding: 20px;
                border-radius: 15px;
                color: white;
                margin-bottom: 10px;">
                <h3>👤 {r['name']}</h3>
                <p>🎯 Score: {r['score']:.2f}</p>
                <p>📅 Experience: {r['experience']}</p>
                <p>🧠 Skills: {', '.join(r['skills'])}</p>
            </div>
            """, unsafe_allow_html=True)

        # -------------------------------
        # PLOTLY CHART
        # -------------------------------
        names = [r['name'] for r in filtered]
        scores = [r['score'] for r in filtered]

        fig = px.bar(x=names, y=scores, title="Resume Ranking")
        st.plotly_chart(fig, use_container_width=True)

        # -------------------------------
        # SAVE
        # -------------------------------
        save_to_db(filtered)

        # -------------------------------
        # EXPORT
        # -------------------------------
        df = pd.DataFrame(filtered)
        st.download_button("📤 Export CSV", df.to_csv(index=False), "results.csv")