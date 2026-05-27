"""
Groq AI Service - LLM-powered resume suggestions using Llama 3
"""

from groq import Groq
from loguru import logger
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.config import settings


def get_groq_client() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_groq(prompt: str, system: str = "", max_tokens: int = 1500) -> str:
    client = get_groq_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) resume coach and career advisor
with 15+ years of experience helping candidates land jobs at top tech companies.
You provide specific, actionable, and concise advice. Always respond in valid JSON format."""


def generate_resume_suggestions(
    resume_text: str,
    job_description: str,
    matched_skills: List[str],
    missing_skills: List[str],
    missing_keywords: List[str],
    ats_score: float,
) -> Dict[str, Any]:
    """Generate comprehensive AI suggestions using Groq Llama 3."""

    prompt = f"""
Analyze this resume against the job description and provide detailed improvement suggestions.

ATS Score: {ats_score}/100
Matched Skills: {', '.join(matched_skills[:15])}
Missing Skills: {', '.join(missing_skills[:15])}
Missing Keywords: {', '.join(missing_keywords[:10])}

JOB DESCRIPTION (first 1500 chars):
{job_description[:1500]}

RESUME (first 1500 chars):
{resume_text[:1500]}

Respond ONLY with this exact JSON structure:
{{
  "missing_skills_tips": [
    "Tip 1 about acquiring or showcasing missing skill",
    "Tip 2",
    "Tip 3",
    "Tip 4",
    "Tip 5"
  ],
  "optimization_tips": [
    "Resume optimization tip 1",
    "Tip 2",
    "Tip 3",
    "Tip 4"
  ],
  "better_bullet_points": [
    "Rewrote bullet: Led development of X resulting in Y% improvement",
    "Rewrote bullet: Architected scalable system handling Z requests/day",
    "Rewrote bullet: Reduced deployment time by N% using CI/CD pipeline"
  ],
  "action_verbs": [
    "Architected", "Spearheaded", "Optimized", "Engineered", "Delivered",
    "Streamlined", "Implemented", "Accelerated", "Transformed", "Launched"
  ],
  "ats_feedback": [
    "ATS optimization tip 1 - be very specific",
    "Tip 2",
    "Tip 3",
    "Tip 4"
  ],
  "project_improvements": [
    "Project improvement suggestion 1",
    "Suggestion 2",
    "Suggestion 3"
  ],
  "overall_summary": "2-3 sentence executive summary of what this candidate should focus on to improve their ATS score and land this role."
}}"""

    try:
        raw = _call_groq(prompt, system=SYSTEM_PROMPT, max_tokens=2000)
        import json, re

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data
        return _fallback_suggestions(missing_skills, missing_keywords, ats_score)
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return _fallback_suggestions(missing_skills, missing_keywords, ats_score)


def generate_rewritten_resume(resume_text: str, job_description: str) -> str:
    """Generate an AI-rewritten resume optimized for the JD."""
    prompt = f"""
Rewrite the following resume to be highly optimized for this job description.
Make it ATS-friendly with strong action verbs, quantified achievements, and relevant keywords.

JOB DESCRIPTION:
{job_description[:1000]}

ORIGINAL RESUME:
{resume_text[:2000]}

Provide the rewritten resume in clean plain text format, keeping the same structure
but improving language, adding missing keywords naturally, and strengthening bullet points.
Start with "OPTIMIZED RESUME:" then the content.
"""
    try:
        return _call_groq(prompt, max_tokens=2500)
    except Exception as e:
        logger.error(f"Resume rewrite error: {e}")
        return "Could not generate rewritten resume. Please try again."


def generate_interview_questions(job_description: str, resume_text: str) -> List[str]:
    """Generate likely interview questions based on JD and resume."""
    prompt = f"""
Based on this job description and resume, generate 10 likely interview questions.
Include technical, behavioral, and situational questions.

JOB DESCRIPTION (first 800 chars): {job_description[:800]}
RESUME (first 800 chars): {resume_text[:800]}

Respond with a JSON array of 10 questions:
["Question 1?", "Question 2?", ...]
"""
    try:
        import json, re
        raw = _call_groq(prompt, max_tokens=1000)
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return []
    except Exception as e:
        logger.error(f"Interview questions error: {e}")
        return []


def compute_interview_readiness(
    ats_score: float,
    skill_overlap: float,
    section_completeness: float,
) -> Dict[str, Any]:
    """Compute interview readiness score."""
    score = (ats_score * 0.5 + skill_overlap * 0.3 + section_completeness * 0.2)
    score = round(min(score, 100), 1)

    if score >= 80:
        level = "High"
        color = "green"
        message = "You are well-prepared for interviews for this role."
    elif score >= 60:
        level = "Medium"
        color = "orange"
        message = "Some preparation needed before applying to this role."
    else:
        level = "Low"
        color = "red"
        message = "Significant work needed before this role is a good match."

    return {"score": score, "level": level, "color": color, "message": message}


def _fallback_suggestions(
    missing_skills: List[str],
    missing_keywords: List[str],
    ats_score: float,
) -> Dict[str, Any]:
    """Fallback suggestions when Groq API is unavailable."""
    return {
        "missing_skills_tips": [
            f"Add '{s}' to your skills section or demonstrate it in project bullets"
            for s in missing_skills[:5]
        ] or ["Review the job description and add relevant missing skills"],
        "optimization_tips": [
            "Use exact keywords from the job description in your resume",
            "Quantify achievements with numbers, percentages, and metrics",
            "Ensure your resume has clear sections: Summary, Experience, Skills, Education",
            "Use industry-standard job titles that match the posting",
        ],
        "better_bullet_points": [
            "Led cross-functional team of 5 engineers to deliver feature X, reducing load time by 40%",
            "Architected microservices infrastructure handling 1M+ daily requests",
            "Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes",
        ],
        "action_verbs": [
            "Architected", "Engineered", "Spearheaded", "Optimized",
            "Delivered", "Launched", "Transformed", "Streamlined",
        ],
        "ats_feedback": [
            "Include more keywords from the job description",
            "Avoid tables and graphics - ATS systems can't parse them",
            "Use standard section headers (Experience, Education, Skills)",
            f"Current ATS score is {ats_score}/100 - focus on adding missing keywords",
        ],
        "project_improvements": [
            "Add GitHub links to your projects",
            "Include tech stack used in each project",
            "Quantify project impact (users, performance improvements, etc.)",
        ],
        "overall_summary": (
            f"Your resume scores {ats_score}/100 on ATS compatibility. "
            "Focus on incorporating missing skills and keywords from the job description. "
            "Quantify your achievements and use strong action verbs to stand out."
        ),
    }
