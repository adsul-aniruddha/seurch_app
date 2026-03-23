import os
import re
from collections import defaultdict

DATA_PATH = "data"

class MiniSearchEngine:
    def __init__(self):
        self.index = defaultdict(set)
        self.documents = {}

    def tokenize(self, text):
        words = re.findall(r"\b[a-z]+\b", text.lower())
        stopwords = {"is", "the", "and", "a", "of", "to"}
        return [w for w in words if w not in stopwords]

    def build_index(self):
        for file in os.listdir(DATA_PATH):
            if file.endswith(".txt"):
                path = os.path.join(DATA_PATH, file)
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    tokens = self.tokenize(text)
                    self.documents[file] = tokens
                    for word in tokens:
                        self.index[word].add(file)

    def search(self, query):
        tokens = self.tokenize(query)
        scores = {}

        for token in tokens:
            for doc in self.index.get(token, []):
                scores[doc] = scores.get(doc, 0) + 1

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
