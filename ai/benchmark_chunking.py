import sys
import os
import io
import re
import json
import statistics
from collections import Counter
from typing import List, Dict, Any, Optional


# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.core.database import SessionLocal
from app.models.document import Document, DocumentVersion

def extract_citation_page(note: Optional[str]) -> Optional[str]:
    """Extract page number from citation tag like [cite: 4] or [cite: 23, 24]"""
    if not note:
        return None
    match = re.search(r'\[cite:\s*([^\]]+)\]', note)
    return match.group(1).strip() if match else None

# =============================================================================
# STRATEGY A: Fixed-size Chunking (Blind sliding window)
# =============================================================================
def chunk_strategy_a_fixed_size(docs: List[Any], chunk_size: int = 200, chunk_overlap: int = 40) -> List[Dict[str, Any]]:
    chunks = []
    for doc in docs:
        version = doc.versions[0] if doc.versions else None
        page = extract_citation_page(version.note if version else None)
        full_text = f"[{doc.category}] [{doc.module}] {doc.title}. {version.content if version else ''} {version.note or ''}".strip()
        
        # Sliding window
        start = 0
        chunk_idx = 1
        text_len = len(full_text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_content = full_text[start:end].strip()
            
            chunks.append({
                "strategy": "A_FixedSize",
                "document_id": doc.id,
                "version_id": version.id if version else None,
                "category": doc.category,
                "module": doc.module,
                "title": doc.title,
                "chunk_index": chunk_idx,
                "content": chunk_content,
                "source": doc.source,
                "page": page,
                "char_count": len(chunk_content),
                "token_est": int(len(chunk_content.split()) * 1.3),
                "is_severed": end < text_len and not chunk_content.endswith(('.', '!', '?'))
            })
            chunk_idx += 1
            if end >= text_len:
                break
            start += (chunk_size - chunk_overlap)
    return chunks

# =============================================================================
# STRATEGY B: Paragraph-based Chunking
# =============================================================================
def chunk_strategy_b_paragraph(docs: List[Any], max_chunk_size: int = 400) -> List[Dict[str, Any]]:
    chunks = []
    for doc in docs:
        version = doc.versions[0] if doc.versions else None
        page = extract_citation_page(version.note if version else None)
        
        # Paragraphs from content and note
        paragraphs = []
        if version and version.content:
            paragraphs.append(version.content.strip())
        if version and version.note:
            paragraphs.append(f"Ghi chú: {version.note.strip()}")
            
        chunk_idx = 1
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}".strip() if current_chunk else para
            else:
                if current_chunk:
                    chunks.append({
                        "strategy": "B_Paragraph",
                        "document_id": doc.id,
                        "version_id": version.id if version else None,
                        "category": doc.category,
                        "module": doc.module,
                        "title": doc.title,
                        "chunk_index": chunk_idx,
                        "content": current_chunk,
                        "source": doc.source,
                        "page": page,
                        "char_count": len(current_chunk),
                        "token_est": int(len(current_chunk.split()) * 1.3),
                        "is_severed": False
                    })
                    chunk_idx += 1
                current_chunk = para
                
        if current_chunk:
            chunks.append({
                "strategy": "B_Paragraph",
                "document_id": doc.id,
                "version_id": version.id if version else None,
                "category": doc.category,
                "module": doc.module,
                "title": doc.title,
                "chunk_index": chunk_idx,
                "content": current_chunk,
                "source": doc.source,
                "page": page,
                "char_count": len(current_chunk),
                "token_est": int(len(current_chunk.split()) * 1.3),
                "is_severed": False
            })
    return chunks

# =============================================================================
# STRATEGY C: Heading/Section-based Chunking
# =============================================================================
def chunk_strategy_c_heading_section(docs: List[Any]) -> List[Dict[str, Any]]:
    chunks = []
    for doc in docs:
        version = doc.versions[0] if doc.versions else None
        page = extract_citation_page(version.note if version else None)
        
        heading = f"# [{doc.category}] [{doc.module}] {doc.title}"
        body = f"{version.content}\n\nLưu ý: {version.note}" if (version and version.note) else (version.content if version else "")
        full_content = f"{heading}\n\n{body}".strip()
        
        chunks.append({
            "strategy": "C_HeadingSection",
            "document_id": doc.id,
            "version_id": version.id if version else None,
            "category": doc.category,
            "module": doc.module,
            "title": doc.title,
            "chunk_index": 1,
            "content": full_content,
            "source": doc.source,
            "page": page,
            "char_count": len(full_content),
            "token_est": int(len(full_content.split()) * 1.3),
            "is_severed": False
        })
    return chunks

# =============================================================================
# STRATEGY D: Structure-Aware Chunking (Runbook Steps + FAQ Q&A Atomic Units)
# =============================================================================
def chunk_strategy_d_structure_aware(docs: List[Any], min_chunk_size: int = 100, max_chunk_size: int = 700) -> List[Dict[str, Any]]:
    chunks = []
    step_pattern = re.compile(r'(?:^|\s)(\d+)\.\s+')
    
    for doc in docs:
        version = doc.versions[0] if doc.versions else None
        page = extract_citation_page(version.note if version else None)
        content = version.content.strip() if version and version.content else ""
        note = version.note.strip() if version and version.note else ""
        
        if doc.category == "FAQ":
            # FAQ: Strictly encapsulate Question + Answer + Note in a single semantic unit
            text = (
                f"# [CÂU HỎI THƯỜNG GẶP] [{doc.module}] {doc.title}\n\n"
                f"Câu hỏi: {doc.title}\n"
                f"Trả lời: {content}"
            )
            if note:
                text += f"\n\nCăn cứ giải đáp: {note}"
            
            chunks.append({
                "strategy": "D_StructureAware",
                "document_id": doc.id,
                "version_id": version.id if version else None,
                "category": doc.category,
                "module": doc.module,
                "title": doc.title,
                "chunk_index": 1,
                "content": text,
                "source": doc.source,
                "page": page,
                "char_count": len(text),
                "token_est": int(len(text.split()) * 1.3),
                "is_severed": False,
                "structure_type": "faq_atomic"
            })
            
        elif doc.category == "RUNBOOK_L1":
            # Runbook: Structure into Problem + Numbered Steps + Escalation
            matches = list(step_pattern.finditer(content))
            if len(matches) >= 2:
                steps = []
                for i in range(len(matches)):
                    start = matches[i].end()
                    end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                    step_text = content[start:end].strip()
                    step_num = matches[i].group(1)
                    steps.append(f"{step_num}. {step_text}")
                formatted_steps = "\n".join(steps)
            else:
                formatted_steps = content
                
            text = (
                f"# [QUY TRÌNH VẬN HÀNH L1] [{doc.module}] {doc.title}\n\n"
                f"Vấn đề sự cố: {doc.title}\n\n"
                f"Các bước khắc phục L1:\n{formatted_steps}"
            )
            if note:
                text += f"\n\nKhuyến cáo & Hotline: {note}"
                
            chunks.append({
                "strategy": "D_StructureAware",
                "document_id": doc.id,
                "version_id": version.id if version else None,
                "category": doc.category,
                "module": doc.module,
                "title": doc.title,
                "chunk_index": 1,
                "content": text,
                "source": doc.source,
                "page": page,
                "char_count": len(text),
                "token_est": int(len(text.split()) * 1.3),
                "is_severed": False,
                "structure_type": "runbook_procedure"
            })
            
        else: # HDSD
            text = f"# [HƯỚNG DẪN SỬ DỤNG] [{doc.module}] {doc.title}\n\nThao tác thực hiện:\n{content}"
            if note:
                text += f"\n\nLưu ý ràng buộc: {note}"
                
            chunks.append({
                "strategy": "D_StructureAware",
                "document_id": doc.id,
                "version_id": version.id if version else None,
                "category": doc.category,
                "module": doc.module,
                "title": doc.title,
                "chunk_index": 1,
                "content": text,
                "source": doc.source,
                "page": page,
                "char_count": len(text),
                "token_est": int(len(text.split()) * 1.3),
                "is_severed": False,
                "structure_type": "hdsd_procedure"
            })
            
    return chunks

def evaluate_strategy(name: str, chunks: List[Dict[str, Any]], total_docs: int = 100) -> Dict[str, Any]:
    char_lens = [c["char_count"] for c in chunks]
    token_ests = [c["token_est"] for c in chunks]
    severed_count = sum(1 for c in chunks if c.get("is_severed", False))
    
    # Calculate how many documents were fragmented into >1 chunk
    doc_chunk_map = Counter([c["document_id"] for c in chunks])
    fragmented_docs = sum(1 for doc_id, count in doc_chunk_map.items() if count > 1)
    
    # Check category distribution
    hdsd_chunks = sum(1 for c in chunks if c["category"] == "HDSD")
    faq_chunks = sum(1 for c in chunks if c["category"] == "FAQ")
    runbook_chunks = sum(1 for c in chunks if c["category"] == "RUNBOOK_L1")
    
    return {
        "name": name,
        "total_chunks": len(chunks),
        "hdsd_chunks": hdsd_chunks,
        "faq_chunks": faq_chunks,
        "runbook_chunks": runbook_chunks,
        "fragmented_docs": fragmented_docs,
        "fragmentation_rate": f"{(fragmented_docs / total_docs) * 100:.1f}%",
        "severed_chunks": severed_count,
        "char_min": min(char_lens),
        "char_max": max(char_lens),
        "char_mean": round(statistics.mean(char_lens), 1),
        "char_median": round(statistics.median(char_lens), 1),
        "token_mean": round(statistics.mean(token_ests), 1),
        "token_max": max(token_ests),
    }

def main():
    print("=" * 85)
    print("THỬ NGHIỆM & ĐÁNH GIÁ 4 CHIẾN LƯỢC CHUNKING CHO MASTERPRO COPILOT")
    print("Dataset: 100 tài liệu thật (50 HDSD | 30 FAQ | 20 RUNBOOK_L1)")
    print("=" * 85)

    db = SessionLocal()
    docs = db.query(Document).order_by(Document.id).all()
    print(f"Đã nạp {len(docs)} tài liệu từ SQL Server MasterDB.\n")

    # Run 4 strategies
    chunks_a = chunk_strategy_a_fixed_size(docs, chunk_size=200, chunk_overlap=40)
    chunks_b = chunk_strategy_b_paragraph(docs, max_chunk_size=400)
    chunks_c = chunk_strategy_c_heading_section(docs)
    chunks_d = chunk_strategy_d_structure_aware(docs)

    db.close()

    # Evaluations
    stats_a = evaluate_strategy("Strategy A (Fixed-size 200/40)", chunks_a)
    stats_b = evaluate_strategy("Strategy B (Paragraph-based)", chunks_b)
    stats_c = evaluate_strategy("Strategy C (Heading/Section)", chunks_c)
    stats_d = evaluate_strategy("Strategy D (Structure-Aware)", chunks_d)

    evaluations = [stats_a, stats_b, stats_c, stats_d]

    # Print Comparative Table
    print("-" * 85)
    print(f"{'Tiêu chí đánh giá':<30} | {'Strategy A':<11} | {'Strategy B':<11} | {'Strategy C':<11} | {'Strategy D':<11}")
    print("-" * 85)
    print(f"{'Tổng số chunks sinh ra':<30} | {stats_a['total_chunks']:<11} | {stats_b['total_chunks']:<11} | {stats_c['total_chunks']:<11} | {stats_d['total_chunks']:<11}")
    print(f"{' - Chunks HDSD':<30} | {stats_a['hdsd_chunks']:<11} | {stats_b['hdsd_chunks']:<11} | {stats_c['hdsd_chunks']:<11} | {stats_d['hdsd_chunks']:<11}")
    print(f"{' - Chunks FAQ':<30} | {stats_a['faq_chunks']:<11} | {stats_b['faq_chunks']:<11} | {stats_c['faq_chunks']:<11} | {stats_d['faq_chunks']:<11}")
    print(f"{' - Chunks RUNBOOK_L1':<30} | {stats_a['runbook_chunks']:<11} | {stats_b['runbook_chunks']:<11} | {stats_c['runbook_chunks']:<11} | {stats_d['runbook_chunks']:<11}")
    print(f"{'Số tài liệu bị cắt rời (>1)':<30} | {stats_a['fragmented_docs']:<11} | {stats_b['fragmented_docs']:<11} | {stats_c['fragmented_docs']:<11} | {stats_d['fragmented_docs']:<11}")
    print(f"{'Tỷ lệ phân mảnh tài liệu':<30} | {stats_a['fragmentation_rate']:<11} | {stats_b['fragmentation_rate']:<11} | {stats_c['fragmentation_rate']:<11} | {stats_d['fragmentation_rate']:<11}")
    print(f"{'Số chunks bị đứt ngang câu':<30} | {stats_a['severed_chunks']:<11} | {stats_b['severed_chunks']:<11} | {stats_c['severed_chunks']:<11} | {stats_d['severed_chunks']:<11}")
    print(f"{'Ký tự trung bình (Mean chars)':<30} | {stats_a['char_mean']:<11} | {stats_b['char_mean']:<11} | {stats_c['char_mean']:<11} | {stats_d['char_mean']:<11}")
    print(f"{'Ký tự Min - Max':<30} | {str(stats_a['char_min']) + '-' + str(stats_a['char_max']):<11} | {str(stats_b['char_min']) + '-' + str(stats_b['char_max']):<11} | {str(stats_c['char_min']) + '-' + str(stats_c['char_max']):<11} | {str(stats_d['char_min']) + '-' + str(stats_d['char_max']):<11}")
    print(f"{'Tokens trung bình (Tokens)':<30} | {stats_a['token_mean']:<11} | {stats_b['token_mean']:<11} | {stats_c['token_mean']:<11} | {stats_d['token_mean']:<11}")
    print("-" * 85)

    # Show Sample Chunk for Strategy D
    print("\n" + "=" * 85)
    print("MẪU CHUNK ĐẠI DIỆN STRATEGY D (ĐẦY ĐỦ METADATA THEO YÊU CẦU)")
    print("=" * 85)
    sample_runbook_chunk = next(c for c in chunks_d if c["category"] == "RUNBOOK_L1")
    print(json.dumps(sample_runbook_chunk, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
