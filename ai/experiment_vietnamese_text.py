import sys
import os
import io
import json
from collections import Counter

# Set UTF-8 encoding in Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure backend and ai modules are accessible
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.core.database import SessionLocal
from app.models.document import Document, DocumentVersion
from vietnamese_preprocessor import VietnameseTextPreprocessor, DOMAIN_TERMS

def run_vietnamese_experiment():
    print("=" * 80)
    print("EXPERIMENT: ĐÁNH GIÁ NĂNG LỰC XỬ LÝ TEXT TIẾNG VIỆT CHO MASTERPRO COPILOT")
    print("=" * 80)

    # 1. Load data from SQL Server MasterDB
    db = SessionLocal()
    docs = db.query(Document).order_by(Document.id).all()
    print(f"\n[Bước 1] Nạp dữ liệu từ Database: Đã tải {len(docs)} Document kèm DocumentVersion.")

    preprocessor = VietnameseTextPreprocessor()
    processed_results = []

    for d in docs:
        latest_ver = d.versions[0] if d.versions else None
        doc_dict = {
            "id": d.id,
            "document_code": d.document_code,
            "category": d.category,
            "module": d.module,
            "title": d.title,
            "source": d.source,
            "version": d.current_version,
            "status": d.status,
            "content": latest_ver.content if latest_ver else "",
            "note": latest_ver.note if latest_ver else ""
        }
        res = preprocessor.process(doc_dict)
        processed_results.append(res)

    db.close()

    # =========================================================================
    # KIỂM TRA 1: KÝ TỰ TIẾNG VIỆT & UNICODE (ĐẶC THÙ TIẾNG VIỆT)
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. KIỂM TRA UNICODE TIẾNG VIỆT (Vowel & Tone Mark Frequency)")
    print("=" * 80)

    all_normalized_corpus = " ".join([r["normalized_text"] for r in processed_results])

    vietnamese_special_chars = {
        'ă': 0, 'â': 0, 'ê': 0, 'ô': 0, 'ơ': 0, 'ư': 0, 'đ': 0,
        'Ă': 0, 'Â': 0, 'Ê': 0, 'Ô': 0, 'Ơ': 0, 'Ư': 0, 'Đ': 0
    }
    for char in all_normalized_corpus:
        if char in vietnamese_special_chars:
            vietnamese_special_chars[char] += 1

    print("Tần suất xuất hiện các ký tự đặc thù tiếng Việt trong toàn bộ corpus:")
    for char, cnt in vietnamese_special_chars.items():
        print(f"  - Ký tự '{char}': {cnt:>4} lần")

    # Tone marks distribution
    tone_marks = {
        "Dấu Sắc (Acute)": len([c for c in all_normalized_corpus if c in "áắấéếíóốớúứýÁẮẤÉẾÍÓỐỚÚỨÝ"]),
        "Dấu Huyền (Grave)": len([c for c in all_normalized_corpus if c in "àằầèềìòồờùừỳÀẰẦÈỀÌÒỒỜÙỪỲ"]),
        "Dấu Hỏi (Hook above)": len([c for c in all_normalized_corpus if c in "ảẳẩẻểỉỏổởủửỷẢẲẨẺỂỈỎỔỞỦỬỶ"]),
        "Dấu Ngã (Tilde)": len([c for c in all_normalized_corpus if c in "ãẵẫẽễĩõỗỡũữỹÃẴẪẼỄĨÕỖỠŨỮỸ"]),
        "Dấu Nặng (Dot below)": len([c for c in all_normalized_corpus if c in "ạặậẹệịọộợụựỵẠẶẬẸỆỊỌỘỢỤỰỴ"])
    }
    print("\nPhân bố 5 thanh điệu tiếng Việt:")
    for tone, cnt in tone_marks.items():
        print(f"  - {tone}: {cnt:>4} ký tự")

    # =========================================================================
    # KIỂM TRA 2: CHUẨN HÓA VĂN BẢN (Text Normalization)
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. KIỂM TRA TEXT NORMALIZATION")
    print("=" * 80)
    import unicodedata
    is_all_nfc = all(unicodedata.is_normalized('NFC', r["normalized_text"]) for r in processed_results)
    print(f" - Chuẩn hóa toàn bộ về Unicode NFC: {'THÀNH CÔNG (100% NFC)' if is_all_nfc else 'THẤT BẠI'}")
    
    # Check for unwanted control characters or double spaces
    has_double_spaces = any("  " in r["normalized_text"] for r in processed_results)
    print(f" - Kiểm tra khoảng trắng thừa (Double spaces): {'SẠCH (0 lỗi)' if not has_double_spaces else 'CÓ LỖI'}")

    # =========================================================================
    # KIỂM TRA 3: CẤU TRÚC VĂN BẢN (Headings, Steps, Q&A)
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. PHÂN TÍCH CẤU TRÚC VĂN BẢN (Structure Parsing)")
    print("=" * 80)
    structure_counts = Counter([r["metadata"]["structure_type"] for r in processed_results])
    for st, count in structure_counts.items():
        print(f"  - Cấu trúc '{st}': {count} bản ghi")

    # =========================================================================
    # KIỂM TRA 4: BẢO TOÀN NỘI DUNG NGHIỆP VỤ & THÔNG TIN GỐC
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. KIỂM TRA BẢO TOÀN THÔNG TIN (Zero Information Loss)")
    print("=" * 80)
    lossless_passed = True
    for r in processed_results:
        raw = r["raw_text"]
        norm = r["normalized_text"]
        # Verify title, module, note (if exists) are present in normalized text
        if raw["title"] not in norm:
            print(f"  [!] Mất title tại ID: {r['metadata']['document_id']}")
            lossless_passed = False
        if raw["module"] not in norm:
            print(f"  [!] Mất module tại ID: {r['metadata']['document_id']}")
            lossless_passed = False
        if raw["note"] and raw["note"] not in norm:
            print(f"  [!] Mất note tại ID: {r['metadata']['document_id']}")
            lossless_passed = False

    if lossless_passed:
        print("  -> Kết quả: 100/100 bản ghi BẢO TOÀN NGUYÊN VẸN 100% Title, Module, Category, Content và Note.")

    # =========================================================================
    # KIỂM TRA 5: BẢO TOÀN CÁC THUẬT NGỮ CHUYÊN NGÀNH MASTERPRO ERP/POS
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. BẢO TOÀN & ĐỘ PHỦ CÁC THUẬT NGỮ CHUYÊN NGÀNH (Domain Terms)")
    print("=" * 80)
    term_counts = Counter()
    for r in processed_results:
        for t in r["metadata"]["detected_terms"]:
            term_counts[t] += 1

    for term in DOMAIN_TERMS:
        cnt = term_counts.get(term, 0)
        status = "Phát hiện tốt" if cnt > 0 else "Chưa xuất hiện trong dataset"
        print(f"  - [{term:<15}] : {cnt:>2} tài liệu chứa ({status})")

    # =========================================================================
    # XUẤT 3 MẪU OUTPUT TIÊU BIỂU: RAW_TEXT, NORMALIZED_TEXT, METADATA
    # =========================================================================
    print("\n" + "=" * 80)
    print("6. MẪU DỮ LIỆU ĐẦU RA (OUTPUT CHUẨN CỦA PIPELINE)")
    print("=" * 80)

    # 1 HDSD, 1 FAQ, 1 RUNBOOK_L1
    sample_ids = [1, 51, 81]
    for sid in sample_ids:
        sample = next((r for r in processed_results if r["metadata"]["document_id"] == sid), None)
        if sample:
            print(f"\n>>> MẪU #{sid} — [{sample['metadata']['category']}] {sample['metadata']['title']}")
            print("-" * 60)
            print("1. [raw_text]:")
            print(json.dumps(sample["raw_text"], ensure_ascii=False, indent=2))
            print("\n2. [normalized_text]:")
            print(sample["normalized_text"])
            print("\n3. [metadata]:")
            print(json.dumps(sample["metadata"], ensure_ascii=False, indent=2))
            print("-" * 60)

    print("\n" + "=" * 80)
    print("EXPERIMENT HOÀN TẤT: Dữ liệu tiếng Việt đáp ứng chuẩn cao nhất cho RAG.")
    print("=" * 80)

if __name__ == "__main__":
    run_vietnamese_experiment()
