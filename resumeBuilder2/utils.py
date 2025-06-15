# util.py

import os
import re
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI  # <-- new import

load_dotenv()

# instantiate the v1+ client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # you can omit this if OPENAI_API_KEY is in your env
)

def get_openai_embedding(text: str, model: str = "text-embedding-ada-002") -> list[float]:
    """
    Get embedding vector for text using OpenAI v1+ Python SDK.
    """
    # note: input may be a single string or list[str]
    resp = client.embeddings.create(
        model=model,
        input=text
    )
    # resp.data is a list of embedding objects
    return resp.data[0].embedding

def cosine_similarity(a: list[float], b: list[float]) -> float:
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_keywords(text: str) -> set[str]:
    words = re.findall(r'\b\w{3,}\b', text.lower())
    return set(words)

def hybrid_resume_job_match_score(
    resume_text: str,
    job_description_text: str,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> tuple[float, float, float]:
    """
    Returns (hybrid, semantic, keyword) scores in [0,100].
    """
    # 1) semantic
    emb_resume = get_openai_embedding(resume_text)
    emb_jd     = get_openai_embedding(job_description_text)
    semantic_score = cosine_similarity(emb_resume, emb_jd) * 100

    # 2) keyword
    ks_resume = get_keywords(resume_text)
    ks_jd     = get_keywords(job_description_text)
    kw_overlap = len(ks_resume & ks_jd) / len(ks_jd) if ks_jd else 0
    keyword_score = kw_overlap * 100

    # 3) hybrid
    hybrid_score = semantic_weight * semantic_score + keyword_weight * keyword_score

    return round(hybrid_score, 2), round(semantic_score, 2), round(keyword_score, 2)
