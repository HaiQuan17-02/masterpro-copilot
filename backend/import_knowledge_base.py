import sys
import os
import io
import argparse

# Ensure UTF-8 output encoding in Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import engine, SessionLocal, Base
from app.data.masterpro_dataset import MASTERPRO_DATASET
from app.services.document_importer import KnowledgeBaseImporter

def main():
    parser = argparse.ArgumentParser(description="Import MasterPro Knowledge Base into SQL Server (MasterDB)")
    parser.add_argument("--version", default="1.0", help="Phiên bản mặc định ban đầu (default: 1.0)")
    parser.add_argument("--status", default="APPROVED", choices=["DRAFT", "APPROVED"], help="Trạng thái ban đầu (default: APPROVED)")
    args = parser.parse_args()

    print("=" * 70)
    print("MASTERPRO COPILOT — KHỞI TẠO & IMPORT KNOWLEDGE BASE")
    print(f"Cấu hình: Version='{args.version}', Status='{args.status}'")
    print("=" * 70)

    # 1. Tạo bảng documents và document_versions nếu chưa có
    print("\n[Bước 1/3] Kiểm tra và khởi tạo bảng 'documents' & 'document_versions'...")
    Base.metadata.create_all(bind=engine)
    print(" -> Các bảng cơ sở dữ liệu đã sẵn sàng.")

    # 2. Khởi tạo session và importer
    print("\n[Bước 2/3] Tiến hành validation và nạp dữ liệu vào Database...")
    db = SessionLocal()
    importer = KnowledgeBaseImporter(db=db, default_version=args.version, default_status=args.status)

    report = importer.import_documents(MASTERPRO_DATASET)
    db.close()

    # 3. Báo cáo kết quả
    print("\n" + "=" * 70)
    print("BÁO CÁO KẾT QUẢ IMPORT KNOWLEDGE BASE")
    print("=" * 70)
    print(f" * Tổng số bản ghi xử lý (Processed) : {report['total_processed']}")
    print(f" * Tổng số Document mới được import : {report['total_documents']}")
    print(f"   - Số HDSD                         : {report['hdsd_count']}")
    print(f"   - Số FAQ                          : {report['faq_count']}")
    print(f"   - Số RUNBOOK_L1                   : {report['runbook_l1_count']}")
    print(f" * Số duplicate bị bỏ qua            : {report['duplicate_count']}")
    print(f" * Số lỗi phát sinh                  : {report['error_count']}")

    if report["errors"]:
        print("\nDanh sách chi tiết các lỗi:")
        for err in report["errors"]:
            print(f"  [X] {err}")
    print("=" * 70)

if __name__ == "__main__":
    main()
