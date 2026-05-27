"""
NLP Pipeline - Resume & JD Parsing, Skill Extraction, Scoring Engine
Uses: spaCy, Sentence Transformers, TF-IDF, cosine similarity
"""

import re
import json
import spacy
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from loguru import logger
from functools import lru_cache

from backend.config import settings
from backend.nlp.skills_database import TECH_SKILLS, SOFT_SKILLS, ALL_SKILLS

# ── Model Loading (cached) ────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_spacy_model():
    try:
        nlp = spacy.load(settings.SPACY_MODEL)
        logger.info(f"✅ spaCy model loaded: {settings.SPACY_MODEL}")
        return nlp
    except OSError:
        logger.warning("spaCy en_core_web_md not found, falling back to en_core_web_sm")
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logger.error("No spaCy model found. Run: python -m spacy download en_core_web_md")
            raise


@lru_cache(maxsize=1)
def load_sentence_transformer():
    try:
        model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        logger.info(f"✅ Sentence Transformer loaded: {settings.SENTENCE_TRANSFORMER_MODEL}")
        return model
    except Exception as e:
        logger.error(f"Failed to load Sentence Transformer: {e}")
        raise


# ── Text Cleaning ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Remove noise and normalize whitespace."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)       # non-ASCII
    text = re.sub(r'\s+', ' ', text)                   # extra whitespace
    text = re.sub(r'[•▪▸◦●]\s*', '- ', text)          # bullet chars
    text = re.sub(r'(http|https)://\S+', '', text)      # URLs
    text = re.sub(r'\S+@\S+', '', text)                 # emails
    text = re.sub(r'\b\d{10}\b', '', text)              # phone numbers
    return text.strip()


# ── Section Detection ─────────────────────────────────────────────────────────

SECTION_HEADERS = {
    "experience":      r'(work\s*experience|professional\s*experience|employment|experience)',
    "education":       r'(education|academic|qualification|degree)',
    "skills":          r'(skills|technical\s*skills|core\s*competencies|expertise)',
    "projects":        r'(projects|personal\s*projects|key\s*projects)',
    "certifications":  r'(certif|credential|license)',
    "summary":         r'(summary|objective|profile|about\s*me)',
    "contact":         r'(contact|phone|email|address|linkedin)',
    "achievements":    r'(achievements|awards|honors|accomplishments)',
    "languages":       r'(languages|language\s*proficiency)',
}

def detect_sections(text: str) -> Dict[str, str]:
    """Split resume text into sections."""
    sections = {}
    lines = text.split('\n')
    current_section = "other"
    current_content = []

    for line in lines:
        line_lower = line.lower().strip()
        matched = False
        for section, pattern in SECTION_HEADERS.items():
            if re.search(pattern, line_lower) and len(line.strip()) < 60:
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = section
                current_content = []
                matched = True
                break
        if not matched:
            current_content.append(line)

    if current_content:
        sections[current_section] = '\n'.join(current_content)

    return sections


def get_section_completeness(sections: Dict[str, str]) -> Tuple[float, List[str]]:
    """Score based on which key sections are present."""
    important = ["experience", "education", "skills", "summary", "contact"]
    bonus     = ["projects", "certifications", "achievements"]
    found = list(sections.keys())

    score = 0.0
    score += sum(20 for s in important if s in found)   # 20 pts each, max 100
    score += sum(5  for s in bonus     if s in found)    # bonus
    score = min(score, 100.0)
    return score, found


# ── Skill Extraction ──────────────────────────────────────────────────────────

def extract_skills(text: str) -> List[str]:
    """Extract skills from text using pattern matching + NLP."""
    text_lower = text.lower()
    found_skills = []

    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    # NLP entity extraction for additional skills
    try:
        nlp = load_spacy_model()
        doc = nlp(text[:50000])  # limit for performance
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"]:
                candidate = ent.text.strip()
                if len(candidate) > 1 and candidate not in found_skills:
                    if any(candidate.lower() in s.lower() for s in ALL_SKILLS):
                        found_skills.append(candidate)
    except Exception as e:
        logger.warning(f"spaCy extraction error: {e}")

    return list(dict.fromkeys(found_skills))  # deduplicate, preserve order


# ── Keyword Extraction (TF-IDF) ───────────────────────────────────────────────

def extract_keywords_tfidf(text: str, top_n: int = 30) -> List[str]:
    """Extract top keywords using TF-IDF."""
    try:
        sentences = [s.strip() for s in re.split(r'[.\n]', text) if len(s.strip()) > 10]
        if len(sentences) < 2:
            sentences = [text[:500], text[500:]]

        vectorizer = TfidfVectorizer(
            max_features=200,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
        top_indices = scores.argsort()[::-1][:top_n]
        return [feature_names[i] for i in top_indices]
    except Exception as e:
        logger.warning(f"TF-IDF extraction error: {e}")
        return []


# ── Semantic Similarity ───────────────────────────────────────────────────────

def compute_semantic_similarity(text1: str, text2: str) -> float:
    """Compute semantic similarity using Sentence Transformers."""
    try:
        model = load_sentence_transformer()
        emb1 = model.encode([text1[:2000]], convert_to_numpy=True)
        emb2 = model.encode([text2[:2000]], convert_to_numpy=True)
        sim = cosine_similarity(emb1, emb2)[0][0]
        return float(np.clip(sim * 100, 0, 100))
    except Exception as e:
        logger.warning(f"Semantic similarity error: {e}")
        return 0.0


def compute_tfidf_similarity(text1: str, text2: str) -> float:
    """Compute TF-IDF cosine similarity between two texts."""
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(np.clip(sim * 100, 0, 100))
    except Exception as e:
        logger.warning(f"TF-IDF similarity error: {e}")
        return 0.0


# ── Formatting Score ──────────────────────────────────────────────────────────

def compute_formatting_score(text: str, sections: Dict) -> float:
    """Heuristic formatting quality score."""
    score = 0.0

    # Length check (ideal: 300–1000 words)
    word_count = len(text.split())
    if 300 <= word_count <= 1200:
        score += 25
    elif word_count > 150:
        score += 12

    # Has bullet points
    if re.search(r'[-•▪]\s', text):
        score += 15

    # Has dates/years (experience markers)
    if re.search(r'\b(19|20)\d{2}\b', text):
        score += 15

    # Has email
    if re.search(r'\S+@\S+\.\S+', text):
        score += 10

    # Has phone
    if re.search(r'[\+\(]?[\d\s\-\(\)]{10,}', text):
        score += 10

    # Has LinkedIn / GitHub
    if re.search(r'linkedin|github', text, re.IGNORECASE):
        score += 10

    # Section variety
    score += min(len(sections) * 3, 15)

    return min(score, 100.0)


# ── Main ATS Scoring Engine ───────────────────────────────────────────────────

def compute_ats_score(
    resume_text: str,
    jd_text: str,
    resume_skills: List[str],
    jd_skills: List[str],
    sections: Dict,
    semantic_sim: float,
    tfidf_sim: float,
) -> Dict[str, Any]:
    """Compute comprehensive ATS score with all sub-metrics."""

    # Skill overlap
    resume_set = {s.lower() for s in resume_skills}
    jd_set     = {s.lower() for s in jd_skills}

    matched_skills  = [s for s in jd_skills if s.lower() in resume_set]
    missing_skills  = [s for s in jd_skills if s.lower() not in resume_set]
    skill_overlap   = (len(matched_skills) / max(len(jd_set), 1)) * 100

    # Keyword match
    resume_keywords = set(extract_keywords_tfidf(resume_text, 50))
    jd_keywords     = set(extract_keywords_tfidf(jd_text, 50))
    matched_kw      = list(resume_keywords & jd_keywords)
    missing_kw      = list(jd_keywords - resume_keywords)
    keyword_match   = (len(matched_kw) / max(len(jd_keywords), 1)) * 100

    # Section completeness
    section_score, found_sections = get_section_completeness(sections)

    # Formatting score
    formatting = compute_formatting_score(resume_text, sections)

    # Resume quality (weighted combo)
    quality = (
        semantic_sim  * 0.30 +
        tfidf_sim     * 0.15 +
        skill_overlap * 0.20 +
        keyword_match * 0.15 +
        section_score * 0.10 +
        formatting    * 0.10
    )

    # Final ATS score (weighted)
    ats_score = (
        semantic_sim  * 0.25 +
        skill_overlap * 0.25 +
        keyword_match * 0.20 +
        tfidf_sim     * 0.10 +
        section_score * 0.10 +
        formatting    * 0.10
    )
    ats_score = min(round(ats_score, 2), 100.0)

    return {
        "ats_score":            ats_score,
        "keyword_match_pct":    round(keyword_match, 2),
        "semantic_similarity":  round(semantic_sim, 2),
        "skill_overlap_pct":    round(skill_overlap, 2),
        "formatting_score":     round(formatting, 2),
        "section_completeness": round(section_score, 2),
        "resume_quality_score": round(quality, 2),
        "matched_skills":       matched_skills,
        "missing_skills":       missing_skills,
        "matched_keywords":     matched_kw[:20],
        "missing_keywords":     missing_kw[:20],
        "sections_found":       found_sections,
    }


# ── Resume Parser ─────────────────────────────────────────────────────────────

def parse_resume(text: str) -> Dict[str, Any]:
    """Full resume parsing pipeline."""
    cleaned = clean_text(text)
    sections = detect_sections(cleaned)
    skills = extract_skills(cleaned)
    keywords = extract_keywords_tfidf(cleaned, 30)
    section_score, found = get_section_completeness(sections)

    # Extract contact info
    contact = {}
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        contact["email"] = email_match.group()

    phone_match = re.search(r'[\+\(]?[\d\s\-\(\)]{10,15}', text)
    if phone_match:
        contact["phone"] = phone_match.group().strip()

    linkedin = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    if linkedin:
        contact["linkedin"] = linkedin.group()

    github = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
    if github:
        contact["github"] = github.group()

    return {
        "skills":          skills,
        "keywords":        keywords,
        "sections":        list(sections.keys()),
        "section_content": sections,
        "contact_info":    contact,
        "word_count":      len(cleaned.split()),
        "section_completeness": section_score,
    }


# ── JD Parser ─────────────────────────────────────────────────────────────────

def parse_job_description(jd_text: str) -> Dict[str, Any]:
    """Parse job description for required skills and keywords."""
    cleaned = clean_text(jd_text)
    skills   = extract_skills(cleaned)
    keywords = extract_keywords_tfidf(cleaned, 40)

    # Extract years of experience required
    exp_match = re.search(r'(\d+)\+?\s*years?\s*(of)?\s*experience', cleaned, re.IGNORECASE)
    required_exp = int(exp_match.group(1)) if exp_match else None

    # Extract education requirements
    edu_keywords = []
    for kw in ["bachelor", "master", "phd", "degree", "mba", "bsc", "msc"]:
        if kw in cleaned.lower():
            edu_keywords.append(kw)

    return {
        "required_skills":    skills,
        "keywords":           keywords,
        "required_experience": required_exp,
        "education_requirements": edu_keywords,
    }
