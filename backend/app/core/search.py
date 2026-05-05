from typing import List
import re

class FullTextSearch:
    @staticmethod
    def build_index(content: str) -> dict:
        """Build simple word index for search."""
        words = re.findall(r'\w+', content.lower())
        index = {}

        for word in words:
            if word not in index:
                index[word] = 0
            index[word] += 1

        return index

    @staticmethod
    def search(query: str, content: str, max_results: int = 5) -> List[dict]:
        """Search content by keyword with context."""
        query_words = set(re.findall(r'\w+', query.lower()))
        lines = content.split('\n')
        results = []

        for line_num, line in enumerate(lines):
            score = sum(1 for word in query_words if word in line.lower())
            if score > 0:
                results.append({
                    "line": line_num + 1,
                    "text": line.strip(),
                    "score": score,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
