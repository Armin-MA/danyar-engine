"""Automated Book Ingestion & Dialectical Harmonizer CLI.

Scans the 'books/' directory for PDF documents, extracts atomic claims,
harmonizes dialectical tensions against existing knowledge graph claims,
and persists updated nodes and relationships.

Usage:
    python ingest_books.py
"""

from __future__ import annotations

import os
import sys
import glob
from pathlib import Path

from src.core.orchestrator import DanyarContainer
from src.mechanics.assimilate_book_pdf import assimilate_book_pdf, BookAssimilationSummary
from src.mechanics.export_llm_digest import export_dialectical_digest


BOOKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "books")


def parse_metadata_from_filename(filename: str) -> tuple[str, str]:
    """Extract book title and author from filename pattern (e.g. 'Author - Title.pdf')."""
    base = Path(filename).stem
    if " - " in base:
        parts = base.split(" - ", 1)
        return parts[1].replace("_", " ").strip(), parts[0].replace("_", " ").strip()
    return base.replace("_", " ").strip(), "ناشناس"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("""
================================================================================
📚 پایپ‌لاین هضم هوشمند کتاب‌های PDF دانیار (Book Assimilation Pipeline)
================================================================================
""")

    # 1. Ensure books directory exists
    os.makedirs(BOOKS_DIR, exist_ok=True)
    pdf_files = glob.glob(os.path.join(BOOKS_DIR, "*.pdf"))

    if not pdf_files:
        print(f"""
[!] پوشه کتاب‌ها خالی است:
    مسیر پوشه: {BOOKS_DIR}

💡 راهنمایی:
    کافی است فایل‌های PDF کتاب‌های مورد نظر خود را داخل پوشه 'books' کپی کنید.
    (پیشنهاد: نام فایل را به صورت 'نویسنده - نام کتاب.pdf' بگذارید).
    سپس مجدداً همین برنامه را اجرا فرمایید.
================================================================================
""")
        return

    print(f"[*] تعداد {len(pdf_files)} کتاب PDF در پوشه 'books' شناسایی شد.\n")

    # 2. Initialize Danyar container and knowledge graph
    container = DanyarContainer(verify_health=False)
    graph_repo = container.graph_repo

    total_claims = 0
    total_contradictions = 0
    total_supports = 0

    # 3. Process each book sequentially
    for idx, pdf_path in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_path)
        title, author = parse_metadata_from_filename(filename)

        print(f"[{idx}/{len(pdf_files)}] در حال پردازش کتاب: «{title}» اثر {author}...")

        summary: BookAssimilationSummary = assimilate_book_pdf(
            pdf_path=pdf_path,
            book_title=title,
            author_name=author,
            domain="business",
            graph_repo=graph_repo,
        )

        print(f"    - صفحات استخراج‌شده: {summary.pages_count}")
        print(f"    - قطعات متنی (Chunks): {summary.chunks_count}")
        print(f"    - گزاره‌های اتمیک استخراج‌شده: {summary.claims_count}")
        print(f"    - نقاط تضاد کشف‌شده با سایر کتاب‌ها: {summary.contradicts_count} (CONTRADICTS)")
        print(f"    - نقاط تایید و اجماع: {summary.supports_count} (SUPPORTS)")
        print("-" * 60)

        total_claims += summary.claims_count
        total_contradictions += summary.contradicts_count
        total_supports += summary.supports_count

    # Export updated dialectical knowledge digest for Claude / ChatGPT / Gemini
    export_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "danyar_knowledge_digest.md")
    export_dialectical_digest(graph_repo, export_path)

    print(f"""
================================================================================
🎉 پردازش تمام کتاب‌ها با موفقیت پایان یافت!
📊 آمار کل دانش افزوده شده:
   - مجموع گزاره‌ها: {total_claims}
   - مجموع تضادهای دیالکتیکی: {total_contradictions}
   - مجموع نقاط اجماع: {total_supports}
📄 فایل خروجی آماده برای تحویل به Claude / ChatGPT / Gemini:
   {export_path}
================================================================================
""")


if __name__ == "__main__":
    main()
