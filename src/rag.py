# ===============================================================
# src/rag.py - RAG SIMPLE CON BM25
# ===============================================================

import re
import numpy as np
from pathlib import Path
from rank_bm25 import BM25Okapi

class SimpleRAG:
    def __init__(self, kb_dir="./kb"):
        self.kb_dir = Path(kb_dir)
        self.docs, self.names = [], []
        for f in self.kb_dir.glob("*.md"):
            text = f.read_text(encoding="utf-8")
            self.docs.append(text)
            self.names.append(f.name)
        self.tokenized = [self._tokenize(t) for t in self.docs]
        self.bm25 = BM25Okapi(self.tokenized)
        print(f"✅ RAG inicializado ({len(self.docs)} docs)")

    def _tokenize(self, text):
        return re.findall(r"\b\w+\b", text.lower())

    def search(self, query, k=3):
        q = self._tokenize(query)
        scores = self.bm25.get_scores(q)
        idxs = np.argsort(scores)[-k:][::-1]
        return [{"filename": self.names[i], "content": self.docs[i]} for i in idxs]
