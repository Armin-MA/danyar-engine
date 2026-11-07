"""Simple One-Command Runner for Danyar Engine.

Executes the Danyar web server locally and automatically opens the browser.
Usage:
    python run.py
"""

from __future__ import annotations

import sys
import time
import threading
import webbrowser
import uvicorn

from src.core.orchestrator import is_neo4j_reachable


def open_browser_delayed(url: str, delay: float = 1.2) -> None:
    """Open default web browser after server initializes."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    port = 8000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    # Detect Neo4j status
    neo4j_online = is_neo4j_reachable()
    db_mode = "پایگاه داده زنده (Neo4j Cluster)" if neo4j_online else "حالت مستقل و تعاملی (Standalone Demo Data)"

    banner = f"""
================================================================================
   دانیار | موتور مشاور هوشمند دیالکتیکی (Danyar Dialectical GraphRAG)
================================================================================
* سرور محلی با موفقیت آماده راه‌اندازی شد.
* آدرس داشبورد در مرورگر شما: {url}
* وضعیت مخزن دانش: {db_mode}
* امکانات فعال: گراف سه‌بعدی نئونی + ویرایشگر مارک‌داون فارسی + چت سقراطی
* برای خروج از برنامه، کلیدهای Ctrl + C را در همین پنجره فشار دهید.
================================================================================
"""
    print(banner)

    # Launch browser automatically in background
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    # Start FastAPI server via uvicorn
    uvicorn.run(
        "src.core.orchestrator:bootstrap_system",
        factory=True,
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
