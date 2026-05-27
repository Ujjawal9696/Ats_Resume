"""
ML Models Manager
=================
Handles downloading, caching, and loading of NLP models:
- spaCy (en_core_web_md)
- Sentence Transformers (all-MiniLM-L6-v2)

Models are downloaded to this directory on first run.
"""

import os
import sys
from pathlib import Path

MODEL_DIR = Path(__file__).parent
SPACY_MODEL = "en_core_web_md"
SENTENCE_MODEL = "all-MiniLM-L6-v2"


def download_all_models():
    """Download all required NLP models."""
    print("="*50)
    print("  Downloading NLP Models")
    print("="*50)

    # 1. spaCy
    print(f"\n[1/2] Downloading spaCy model: {SPACY_MODEL}")
    try:
        import spacy
        try:
            spacy.load(SPACY_MODEL)
            print(f"  ✅ {SPACY_MODEL} already installed")
        except OSError:
            os.system(f"{sys.executable} -m spacy download {SPACY_MODEL}")
            print(f"  ✅ {SPACY_MODEL} downloaded")
    except ImportError:
        print("  ❌ spacy not installed. Run: pip install spacy")

    # 2. Sentence Transformers
    print(f"\n[2/2] Downloading Sentence Transformer: {SENTENCE_MODEL}")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(SENTENCE_MODEL, cache_folder=str(MODEL_DIR))
        test = model.encode(["test"])
        print(f"  ✅ {SENTENCE_MODEL} ready (dim={test.shape[1]})")
    except ImportError:
        print("  ❌ sentence-transformers not installed. Run: pip install sentence-transformers")
    except Exception as e:
        print(f"  ⚠ Error: {e}")

    print("\n" + "="*50)
    print("  All models ready!")
    print("="*50)


def get_model_info():
    """Print info about installed models."""
    info = {"spacy": "Not installed", "sentence_transformer": "Not installed"}

    try:
        import spacy
        nlp = spacy.load(SPACY_MODEL)
        info["spacy"] = f"{SPACY_MODEL} ({len(nlp.vocab)} vocab, {nlp.meta.get('vectors', {}).get('width', 0)}d vectors)"
    except Exception:
        pass

    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(SENTENCE_MODEL, cache_folder=str(MODEL_DIR))
        dim = model.encode(["test"]).shape[1]
        info["sentence_transformer"] = f"{SENTENCE_MODEL} ({dim}d embeddings)"
    except Exception:
        pass

    print("\n📋 Model Status:")
    for name, status in info.items():
        icon = "✅" if "Not" not in status else "❌"
        print(f"  {icon} {name}: {status}")

    return info


if __name__ == "__main__":
    download_all_models()
    get_model_info()
