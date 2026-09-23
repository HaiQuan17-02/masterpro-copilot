from typing import List, Dict, Any, Optional
import re

class DocumentChunker:
    """
    Chunker implementation for MasterPro Copilot.
    Supports recursive splitting by headings, paragraphs, and sentence boundaries
    with chunk overlap and metadata preservation.
    """
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not text:
            return []

        base_meta = metadata or {}
        # Split by double newline (paragraphs)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        
        chunks = []
        current_chunk = ""
        chunk_idx = 1

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, chunk_idx, base_meta))
                    chunk_idx += 1
                    # Retain overlap from end of previous chunk
                    overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                    current_chunk = overlap_text + "\n\n" + para if overlap_text else para
                else:
                    # Paragraph itself is larger than chunk_size, split by sentences or slice
                    sub_chunks = self._split_large_paragraph(para)
                    for sc in sub_chunks:
                        chunks.append(self._create_chunk(sc, chunk_idx, base_meta))
                        chunk_idx += 1
                    current_chunk = ""

        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, chunk_idx, base_meta))

        return chunks

    def _split_large_paragraph(self, para: str) -> List[str]:
        # Split by sentence enders
        sentences = re.split(r'(?<=[.!?])\s+', para)
        result = []
        curr = ""
        for s in sentences:
            if len(curr) + len(s) + 1 <= self.chunk_size:
                curr = (curr + " " + s).strip()
            else:
                if curr:
                    result.append(curr)
                curr = s
        if curr:
            result.append(curr)
        return result

    def _create_chunk(self, content: str, index: int, metadata: Dict[str, Any]) -> Dict[str, Any]:
        doc_name = metadata.get("document", "unknown_doc")
        chunk_id = f"{doc_name}_chunk_{index:03d}"
        return {
            "chunk_id": chunk_id,
            "content": content,
            "char_count": len(content),
            "approx_tokens": int(len(content) / 3.5),
            "metadata": {
                **metadata,
                "chunk_index": index
            }
        }
