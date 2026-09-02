import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from data import get_data
from gemini import Gemini


def get_relevant_jobs(jobs: list[str], gemini: Gemini):
    """Retrieve jobs having a higher similarity with the summary

    Args:
        jobs (list[str]): Scraped job data
        gemini (Gemini): Gemini service

    Returns:
        list[str]: Jobs having a higher similarity with the user's summary
    """
    print("Extracting relevant jobs")
    relevant: list[str] = []

    job_embedding = gemini.embed(jobs)
    summary_embedding = np.array(
        gemini.embed(str(get_data("summary")))[0].values
    ).reshape(1, -1)

    for i in range(len(job_embedding)):
        job_vec = np.array(job_embedding[i].values).reshape(1, -1)
        score = cosine_similarity(summary_embedding, job_vec)[0][0]

        if score > 0.5:
            relevant.append(jobs[i])

    return relevant
