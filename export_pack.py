"""CLI Tool to Export Danyar Knowledge Pack for External LLMs.

Generates 'danyar_knowledge_pack.md' ready to be uploaded or pasted into
Claude (claude.ai), ChatGPT (chatgpt.com), or Gemini (gemini.google.com).

Usage:
    python export_pack.py
"""

from __future__ import annotations

import os
import sys

from src.core.orchestrator import DanyarContainer
from src.mechanics.export_knowledge_pack import export_knowledge_pack


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("""
================================================================================
📦 تولید بسته دانشی دیالکتیکی دانیار (Knowledge Pack Exporter)
================================================================================
""")

    container = DanyarContainer(verify_health=False)
    graph_repo = container.graph_repo

    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "danyar_knowledge_pack.md")

    print("[*] در حال واکشی ساختار گراف و سنتز تضادهای فکری...")
    stats = export_knowledge_pack(graph_repo=graph_repo, output_path=output_file)

    print(f"""
[+] بسته دانشی با موفقیت در فایل زیر ایجاد شد:
    مسیر فایل: {stats['output_path']}

📊 آمار بسته تولیدشده:
    - تعداد کل گره‌های گراف: {stats['nodes_count']}
    - تعداد گزاره‌های استخراج‌شده: {stats['claims_count']}
    - تعداد تضادهای فکری ماتریس: {stats['tensions_count']} (CONTRADICTS)
    - تعداد نقاط اجماع: {stats['supports_count']} (SUPPORTS)

💡 نحوه استفاده در کلود، چت‌جی‌پی‌تی یا جمینای:
    ۱. وارد سایت Claude.ai، ChatGPT یا Gemini شوید.
    ۲. فایل 'danyar_knowledge_pack.md' را داخل چت آپلود (یا متنش را کپی) کنید.
    ۳. سوال یا چالش کسب‌وکاری خود را بپرسید!
       مدل هوش مصنوعی بر اساس تضادهای استخراج‌شده بین صاحب‌نظران پاسخ خواهد داد.
================================================================================
""")


if __name__ == "__main__":
    main()
