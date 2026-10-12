"""
Citation Validator Module for MasterPro Copilot (Week 6).

Inspects generated answers, verifies validity of [cite: ...] anchors against
retrieved context chunks, and calculates Groundedness Score.
"""

import re
from typing import List, Dict, Any, Tuple

class CitationValidator:
    """
    Validates groundedness of citations in generated answers.
    """
    CITATION_REGEX = re.compile(r'\[cite:\s*([^\]]+)\]', re.IGNORECASE)

    @classmethod
    def validate(cls, answer: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        citations_found = cls.CITATION_REGEX.findall(answer)
        if not context_chunks:
            return {
                "is_grounded": len(citations_found) == 0,
                "total_citations": len(citations_found),
                "valid_citations": 0,
                "invalid_citations": len(citations_found),
                "groundedness_score": 0.0 if citations_found else 1.0,
                "details": "Không có ngữ cảnh nào được cung cấp."
            }

        # Build set of valid document IDs, pages, and titles from context
        valid_doc_ids = {str(c.get("document_id", "")).lower() for c in context_chunks if c.get("document_id")}
        valid_titles = {str(c.get("title", "")).lower() for c in context_chunks if c.get("title")}
        valid_pages = {str(c.get("page", "")).lower() for c in context_chunks if c.get("page")}

        valid_count = 0
        invalid_list = []

        for cite_str in citations_found:
            cite_lower = cite_str.lower().strip()
            # 1. Check if any valid doc_id appears in citation
            matched_doc = any(doc_id in cite_lower for doc_id in valid_doc_ids if doc_id)
            # 2. Check if valid title appears in citation
            matched_title = any(t in cite_lower for t in valid_titles if len(t) >= 4)
            # 3. Check if citation is an exact valid page number or contains valid page
            matched_page = (cite_lower in valid_pages) or any(
                f"trang {p}" in cite_lower or f"trang: {p}" in cite_lower
                for p in valid_pages if p and p != "none"
            )
            # 4. Check if citation existed natively inside the source chunk content
            in_source = any(
                cite_lower in (c.get("content") or "").lower()
                for c in context_chunks
            )

            if matched_doc or matched_title or matched_page or in_source:
                valid_count += 1
            else:
                invalid_list.append(cite_str)

        total = len(citations_found)
        score = (valid_count / total) if total > 0 else (1.0 if not context_chunks else 0.5)

        return {
            "is_grounded": len(invalid_list) == 0 and total > 0,
            "total_citations": total,
            "valid_citations": valid_count,
            "invalid_citations": len(invalid_list),
            "invalid_details": invalid_list,
            "groundedness_score": round(score, 3)
        }
