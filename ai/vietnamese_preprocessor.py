import re
import unicodedata
from typing import Dict, Any, List, Optional, Tuple


# Core MasterPro Enterprise ERP/POS domain terminology to verify & preserve
DOMAIN_TERMS = [
    "POS",
    "ERP",
    "SKU",
    "barcode",
    "mã vạch",
    "tồn kho",
    "công nợ",
    "phiếu nhập",
    "phiếu xuất",
    "khuyến mãi",
    "chi nhánh",
    "phân quyền",
    "sổ quỹ",
    "số quỹ",
    "khóa sổ",
    "kết số",
    "điểm tích lũy",
    "thành phẩm",
    "bảng giá"
]

class VietnameseTextPreprocessor:
    """
    Vietnamese Text Preprocessing Pipeline for MasterPro Copilot.
    
    Stages:
    1. Unicode Normalization (NFC standard)
    2. Punctuation & Arrow standardization
    3. Structural formatting (Headings, Paragraphs, Numbered Steps, FAQ Q&A, Runbook steps)
    4. Domain terminology detection & preservation check
    5. Structured Output generation (raw_text, normalized_text, metadata)
    """

    def __init__(self):
        # Regex to detect numbered steps: e.g. "1. Kiểm tra... 2. Nhập... 3. Bấm..."
        self.step_pattern = re.compile(r'(?:^|\s)(\d+)\.\s+')
        # Regex for breadcrumb arrows
        self.arrow_pattern = re.compile(r'\s*(?:->|-->|→|➔)\s*')

    def normalize_unicode(self, text: str) -> str:
        """Ensure standard Unicode NFC (Normalization Form C - Precomposed)."""
        if not text:
            return ""
        # Convert decomposed accents (NFD) to precomposed (NFC)
        text = unicodedata.normalize('NFC', text)
        return text

    def clean_whitespace(self, text: str) -> str:
        """Normalizes irregular spaces, tabs, and multi-line breaks."""
        if not text:
            return ""
        # Normalize non-breaking spaces and tabs
        text = text.replace('\xa0', ' ').replace('\t', ' ')
        # Collapse multiple horizontal spaces
        text = re.sub(r'[ ]{2,}', ' ', text)
        # Collapse 3+ newlines into double newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def standardize_punctuation(self, text: str) -> str:
        """Standardizes quotation marks, dashes, and directional arrows."""
        if not text:
            return ""
        # Standardize curly quotes
        text = text.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
        # Standardize navigation arrows to clean '->'
        text = self.arrow_pattern.sub(' -> ', text)
        return text

    def detect_domain_terms(self, text: str) -> List[str]:
        """Identifies domain terminology present in text."""
        text_lower = text.lower()
        found = []
        for term in DOMAIN_TERMS:
            if term.lower() in text_lower:
                found.append(term)
        return found

    def format_numbered_steps(self, content: str) -> Tuple[str, str]:
        """
        Parses inline numbered sequences like '1. Làm A. 2. Làm B. 3. Làm C.'
        and transforms them into clean Markdown ordered lists.
        """

        # Check if content has numbered steps pattern like "1. ... 2. ... "
        matches = list(self.step_pattern.finditer(content))
        if len(matches) >= 2:
            steps = []
            for i in range(len(matches)):
                start = matches[i].end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                step_text = content[start:end].strip()
                step_num = matches[i].group(1)
                steps.append(f"{step_num}. {step_text}")
            formatted = "\n".join(steps)
            return formatted, "numbered_steps"
        return content, "paragraph"

    def process(self, doc_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full pipeline on a raw document dictionary.
        Returns:
            {
                "raw_text": {...},
                "normalized_text": "...",
                "metadata": {...}
            }
        """
        category = self.normalize_unicode(str(doc_item.get("category", "")).strip())
        module = self.normalize_unicode(str(doc_item.get("module", "")).strip())
        title = self.normalize_unicode(str(doc_item.get("title", "")).strip())
        content = self.normalize_unicode(str(doc_item.get("content", "")).strip())
        note = self.normalize_unicode(str(doc_item.get("note", "")).strip()) if doc_item.get("note") else None

        # Clean whitespace and standardize punctuation
        title_clean = self.clean_whitespace(self.standardize_punctuation(title))
        content_clean = self.clean_whitespace(self.standardize_punctuation(content))
        note_clean = self.clean_whitespace(self.standardize_punctuation(note)) if note else None

        # Structure formatting based on Category
        structure_type = "standard"
        if category == "RUNBOOK_L1":
            formatted_steps, st_type = self.format_numbered_steps(content_clean)
            structure_type = st_type
            normalized_body = (
                f"# [QUY TRÌNH VẬN HÀNH L1] [{module}] {title_clean}\n\n"
                f"Các bước thực hiện:\n"
                f"{formatted_steps}"
            )
            if note_clean:
                normalized_body += f"\n\nLưu ý kỹ thuật: {note_clean}"

        elif category == "FAQ":
            structure_type = "qa_pair"
            normalized_body = (
                f"# [CÂU HỎI THƯỜNG GẶP] [{module}] {title_clean}\n\n"
                f"Câu hỏi: {title_clean}\n"
                f"Trả lời: {content_clean}"
            )
            if note_clean:
                normalized_body += f"\n\nCăn cứ giải đáp: {note_clean}"

        else: # HDSD
            # Check for navigation path breadcrumbs
            if " -> " in content_clean:
                structure_type = "procedure_with_breadcrumb"
            else:
                structure_type = "procedure"

            normalized_body = (
                f"# [HƯỚNG DẪN SỬ DỤNG] [{module}] {title_clean}\n\n"
                f"Thao tác nghiệp vụ:\n"
                f"{content_clean}"
            )
            if note_clean:
                normalized_body += f"\n\nLưu ý nghiệp vụ: {note_clean}"

        # Combine text to analyze domain terms
        full_text_for_terms = f"{title_clean} {content_clean} {note_clean or ''}"
        detected_terms = self.detect_domain_terms(full_text_for_terms)

        # Words and characters count
        words = normalized_body.split()

        return {
            "raw_text": {
                "category": doc_item.get("category"),
                "module": doc_item.get("module"),
                "title": doc_item.get("title"),
                "content": doc_item.get("content"),
                "note": doc_item.get("note")
            },
            "normalized_text": normalized_body,
            "metadata": {
                "document_id": doc_item.get("id"),
                "document_code": doc_item.get("document_code"),
                "category": category,
                "module": module,
                "title": title_clean,
                "source": doc_item.get("source", "Tài liệu vận hành MasterPro"),
                "version": doc_item.get("current_version", doc_item.get("version", "1.0")),
                "status": doc_item.get("status", "APPROVED"),
                "note": note_clean,
                "structure_type": structure_type,
                "detected_terms": detected_terms,
                "char_count": len(normalized_body),
                "word_count": len(words),
                "approx_tokens": int(len(words) * 1.3)
            }
        }

Tuple_Text_Structure = tuple
