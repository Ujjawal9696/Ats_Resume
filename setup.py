"""
Setup script - Downloads NLP models and verifies installation
Run this once after installing requirements.txt
"""

import subprocess
import sys


def run(cmd):
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0


def main():
    print("\n" + "="*55)
    print("  ATS Resume Scorer — Setup & Model Download")
    print("="*55)

    print("\n[1/3] Downloading spaCy en_core_web_md model...")
    ok = run(f"{sys.executable} -m spacy download en_core_web_md")
    if not ok:
        print("  ⚠ en_core_web_md failed, trying en_core_web_sm...")
        run(f"{sys.executable} -m spacy download en_core_web_sm")

    print("\n[2/3] Downloading NLTK data...")
    try:
        import nltk
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt", quiet=True)
        nltk.download("wordnet", quiet=True)
        print("  ✓ NLTK data downloaded")
    except Exception as e:
        print(f"  ⚠ NLTK error (non-fatal): {e}")

    print("\n[3/3] Pre-loading Sentence Transformer model...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        _ = model.encode(["test sentence"])
        print("  ✓ Sentence Transformer model ready")
    except Exception as e:
        print(f"  ⚠ Sentence Transformer error: {e}")
        print("    It will auto-download on first use")

    print("\n" + "="*55)
    print("  ✅ Setup complete!")
    print("="*55)
    print("\nNext steps:")
    print("  1. Copy .env.example → .env and fill in your API keys")
    print("  2. Run schema.sql in your Supabase SQL Editor")
    print("  3. Run start_backend.bat  (or: uvicorn backend.main:app --reload)")
    print("  4. Run start_frontend.bat (or: streamlit run frontend/streamlit_app.py)")
    print("  5. Open http://localhost:8501\n")


if __name__ == "__main__":
    main()
