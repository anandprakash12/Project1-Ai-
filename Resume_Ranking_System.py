# AI Resume Ranking Dashboard
import streamlit as st
import PyPDF2
import re
import torch
import pandas as pd
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

# Page Config
st.set_page_config(page_title="AI Resume Ranking System", layout="wide")

# Load BERT Model
@st.cache_resource
def load_model():
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    return tokenizer, model

tokenizer, model = load_model()

# Extract Text
def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

# Preprocess
def preprocess(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    return text

# BERT Embedding
def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt',
                       truncation=True,
                       padding=True,
                       max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    return outputs.last_hidden_state.mean(dim=1)

# Similarity
def similarity(a, b):
    return cosine_similarity(a.numpy(), b.numpy())[0][0]

# Skill Extraction (Basic)
skills_db = [
    "python","sql","excel","machine learning","deep learning",
    "tableau","power bi","nlp","tensorflow","pandas","numpy"
]

def extract_skills(text):
    return [s for s in skills_db if s in text]

# Experience Extraction
def extract_experience(text):
    match = re.findall(r'(\d+)\s+years', text)
    return match[0] + " yrs" if match else "Fresher"

# Header
st.title("AI Resume Ranking System")
st.caption("Professional Dashboard using BERT")

# Inputs
job_desc = st.text_area("Enter Job Description")
files = st.file_uploader("Upload Resumes", accept_multiple_files=True)

# Process Button
if st.button("Analyze Resumes"):

    if not job_desc or not files:
        st.warning("Please enter job description and upload resumes")
    else:
        resumes_data = []
        jd_clean = preprocess(job_desc)
        jd_emb = get_embedding(jd_clean)

        for file in files:
            text = extract_text(file)
            clean = preprocess(text)
            emb = get_embedding(clean)
            score = similarity(emb, jd_emb)

            resumes_data.append({
                "name": file.name,
                "score": score,
                "skills": extract_skills(clean),
                "experience": extract_experience(clean)
            })

        # Sort
        resumes_data = sorted(resumes_data, key=lambda x: x["score"], reverse=True)

        # Dashboard Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Resumes", len(resumes_data))
        col2.metric("Processed", len(resumes_data))
        col3.metric("Success Rate", "100%")

        st.divider()

        # Search
        search = st.text_input("Search by skill or keyword")

        if search:
            resumes_data = [r for r in resumes_data if search.lower() in str(r).lower()]

        # Display Cards
        st.subheader("Ranked Candidates")

        for i, r in enumerate(resumes_data):
            col1, col2 = st.columns([4,1])

            with col1:
                st.markdown(f"### {r['name']}")
                st.write(f"Skills: {', '.join(r['skills'])}")
                st.write(f"Experience: {r['experience']}")

            with col2:
                st.metric("Score", f"{r['score']:.2f}")
                st.progress(float(r['score']))

            st.divider()

        # Export CSV
        df = pd.DataFrame(resumes_data)
        st.download_button("Export Results", df.to_csv(index=False), "results.csv")