"""
EDA & Data Pipeline Notebook
=============================
Resume Dataset Analysis + ATS Scoring Pipeline

Run this notebook to:
1. Load resume & JD datasets
2. Clean and preprocess text
3. Extract features
4. Train/evaluate ATS scoring
5. Visualize results
"""

# %% [1] Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import warnings
warnings.filterwarnings('ignore')

print("✅ All imports loaded")


# %% [2] Sample Resume Dataset
# Replace with your actual dataset path
# dataset = pd.read_csv("your_dataset.csv")

# Using sample data for demonstration
sample_resumes = [
    {
        "resume_text": "Python developer with 5 years experience in Django, FastAPI, PostgreSQL. Built scalable microservices handling 1M+ requests/day. AWS certified.",
        "job_description": "Looking for a Python developer with experience in Django or FastAPI, PostgreSQL, AWS. 3+ years experience required.",
        "match_score": 88,
        "match_label": "high"
    },
    {
        "resume_text": "Frontend engineer skilled in React, Next.js, TypeScript. Built responsive dashboards with Plotly and D3.js. 3 years experience.",
        "job_description": "Senior Python backend developer needed. Must have experience with Django, REST APIs, Docker, Kubernetes.",
        "match_score": 25,
        "match_label": "low"
    },
    {
        "resume_text": "Full-stack developer: React, Node.js, Python, MongoDB, Docker. Led team of 4 engineers. Agile/Scrum methodology.",
        "job_description": "Full-stack engineer with React and Python experience. MongoDB knowledge preferred. Agile experience required.",
        "match_score": 82,
        "match_label": "high"
    },
    {
        "resume_text": "Data scientist with expertise in TensorFlow, PyTorch, scikit-learn. Published 3 research papers on NLP. PhD in Computer Science.",
        "job_description": "Machine Learning Engineer - TensorFlow, PyTorch required. NLP experience preferred. MS/PhD preferred.",
        "match_score": 91,
        "match_label": "high"
    },
    {
        "resume_text": "Marketing manager with 10 years in digital marketing, SEO, Google Ads. MBA from top university.",
        "job_description": "Software Engineer needed with C++, Python, and system design skills. 5+ years experience.",
        "match_score": 8,
        "match_label": "low"
    },
]

dataset = pd.DataFrame(sample_resumes)
print(f"✅ Dataset loaded: {len(dataset)} records")
print(dataset.head())


# %% [3] Data Cleaning
def clean_text(text):
    """Clean and normalize text."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(http|https)://\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    return text.strip().lower()

dataset['clean_resume'] = dataset['resume_text'].apply(clean_text)
dataset['clean_jd'] = dataset['job_description'].apply(clean_text)
dataset['resume_word_count'] = dataset['clean_resume'].apply(lambda x: len(x.split()))
dataset['jd_word_count'] = dataset['clean_jd'].apply(lambda x: len(x.split()))

print("✅ Text cleaned")
print(dataset[['resume_word_count', 'jd_word_count', 'match_score']].describe())


# %% [4] EDA - Score Distribution
fig = px.histogram(
    dataset, x='match_score', nbins=20,
    title='ATS Match Score Distribution',
    color='match_label',
    color_discrete_map={'high': '#10b981', 'medium': '#f59e0b', 'low': '#ef4444'},
    template='plotly_dark',
)
fig.update_layout(
    xaxis_title='Match Score',
    yaxis_title='Count',
    font_family='Inter',
)
fig.show()
print("✅ Score distribution plotted")


# %% [5] EDA - Word Count Analysis
fig = px.scatter(
    dataset, x='resume_word_count', y='match_score',
    color='match_label', size='jd_word_count',
    title='Resume Word Count vs Match Score',
    template='plotly_dark',
    color_discrete_map={'high': '#10b981', 'medium': '#f59e0b', 'low': '#ef4444'},
)
fig.show()
print("✅ Word count analysis plotted")


# %% [6] TF-IDF Similarity Computation
def compute_tfidf_similarity(text1, text2):
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(sim * 100, 2)

dataset['tfidf_similarity'] = dataset.apply(
    lambda row: compute_tfidf_similarity(row['clean_resume'], row['clean_jd']), axis=1
)

print("✅ TF-IDF similarities computed")
print(dataset[['match_score', 'tfidf_similarity', 'match_label']])


# %% [7] Correlation Analysis
fig = px.scatter(
    dataset, x='tfidf_similarity', y='match_score',
    color='match_label', trendline='ols',
    title='TF-IDF Similarity vs Manual Match Score',
    template='plotly_dark',
    color_discrete_map={'high': '#10b981', 'medium': '#f59e0b', 'low': '#ef4444'},
)
fig.show()

corr = dataset[['match_score', 'tfidf_similarity']].corr()
print(f"\n📊 Correlation: {corr.iloc[0, 1]:.4f}")


# %% [8] Skill Extraction Pipeline
TECH_SKILLS = [
    "python", "javascript", "react", "django", "fastapi", "node.js",
    "postgresql", "mongodb", "docker", "kubernetes", "aws", "tensorflow",
    "pytorch", "scikit-learn", "typescript", "next.js", "plotly", "d3.js",
    "nlp", "c++", "agile", "scrum", "rest api", "microservices",
]

def extract_skills(text):
    text_lower = text.lower()
    found = [skill for skill in TECH_SKILLS if re.search(r'\b' + re.escape(skill) + r'\b', text_lower)]
    return found

dataset['resume_skills'] = dataset['clean_resume'].apply(extract_skills)
dataset['jd_skills'] = dataset['clean_jd'].apply(extract_skills)
dataset['matched_skills'] = dataset.apply(
    lambda row: list(set(row['resume_skills']) & set(row['jd_skills'])), axis=1
)
dataset['missing_skills'] = dataset.apply(
    lambda row: list(set(row['jd_skills']) - set(row['resume_skills'])), axis=1
)
dataset['skill_overlap_pct'] = dataset.apply(
    lambda row: len(row['matched_skills']) / max(len(row['jd_skills']), 1) * 100, axis=1
)

print("✅ Skills extracted")
for _, row in dataset.iterrows():
    print(f"\n  Score: {row['match_score']} | Overlap: {row['skill_overlap_pct']:.0f}%")
    print(f"  Matched: {row['matched_skills']}")
    print(f"  Missing: {row['missing_skills']}")


# %% [9] Data Quality Checks
print("\n" + "="*50)
print("📋 DATA QUALITY REPORT")
print("="*50)
print(f"  Total records:     {len(dataset)}")
print(f"  Duplicates:        {dataset.duplicated().sum()}")
print(f"  Null values:       {dataset.isnull().sum().sum()}")
print(f"  Score range:       {dataset['match_score'].min()} – {dataset['match_score'].max()}")
print(f"  Invalid scores:    {((dataset['match_score'] < 0) | (dataset['match_score'] > 100)).sum()}")
print(f"  Avg resume words:  {dataset['resume_word_count'].mean():.0f}")
print(f"  Avg JD words:      {dataset['jd_word_count'].mean():.0f}")

# Remove duplicates and invalid scores
dataset_clean = dataset[
    (dataset['match_score'] >= 0) &
    (dataset['match_score'] <= 100) &
    (~dataset.duplicated())
].copy()
print(f"\n  Clean records:     {len(dataset_clean)}")
print("✅ Data quality checks passed")


# %% [10] Label Normalization
def normalize_label(score):
    if score >= 70: return "high"
    elif score >= 40: return "medium"
    return "low"

dataset_clean['match_label'] = dataset_clean['match_score'].apply(normalize_label)
print("\n✅ Labels normalized:")
print(dataset_clean['match_label'].value_counts())


# %% [11] Export Clean Dataset
output_cols = ['resume_text', 'job_description', 'match_score', 'match_label',
               'tfidf_similarity', 'skill_overlap_pct', 'matched_skills', 'missing_skills']
# dataset_clean[output_cols].to_csv("clean_dataset.csv", index=False)
print("\n✅ Pipeline complete! Ready for ATS scoring.")
print(dataset_clean[output_cols].to_string())
