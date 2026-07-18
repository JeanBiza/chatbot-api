import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

FAQ_PATH = "data/faq.json"
THRESHOLD = 0.75
MODEL_NAME = "all-MiniLM-L6-v2"

class IntentDetector:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.faqs = self._load_faqs()
        self.questions = [f["question"] for f in self.faqs]
        self.embeddings = self.model.encode(self.questions)

    def _load_faqs(self) -> list:
        with open(FAQ_PATH, "r") as f:
            return json.load(f)["faqs"]

    def match(self, user_message: str) -> str | None:
        user_embedding = self.model.encode([user_message])
        similarities = cosine_similarity(user_embedding, self.embeddings)[0]
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score >= THRESHOLD:
            return self.faqs[best_idx]["answer"]
        return None